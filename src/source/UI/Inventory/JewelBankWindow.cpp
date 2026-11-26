#include "stdafx.h"
#include "UI/Inventory/JewelBankWindow.h"

#include "Audio/DSPlaySound.h"
#include "Core/Utilities/StringUtils.h"
#include "Engine/Object/ZzzInfomation.h"
#include "Engine/Object/ZzzInventory.h"
#include "GameLogic/Items/JewelBank.h"
#include "I18N/All.h"
#include "UI/Core/WindowSystem.h"
#include "UI/Dialogs/GenericConfirmDialog.h"
#include "UI/RmlBridge/RmlDocumentVisibility.h"
#include "UI/RmlBridge/RmlNativeTextSize.h"
#include "UI/RmlBridge/RmlPointer.h"
#include "UI/RmlBridge/RmlSyncField.h"
#include "UI/RmlBridge/RmlWindowClose.h"

#include <RmlUi/Core/ElementDocument.h>

#include <limits>
#include <utility>

using namespace SEASON3B;
using namespace mu::ui::window;

namespace
{
namespace JewelBank = GameLogic::Items::JewelBank;

// The amount field takes the digits of the largest amount a withdraw request carries (2147483647).
constexpr int AmountFieldDigits = std::numeric_limits<int32_t>::digits10 + 1;
constexpr float LayerDepth = 4.4f;

Rml::String JewelName(const JewelBank::Entry& entry)
{
    const int type = static_cast<int>(ITEMINDEX(entry.itemGroup, entry.itemNumber));
    if (ItemAttribute == nullptr || type < 0 || type >= MAX_ITEM)
    {
        return {};
    }

    return StringUtils::WideToNarrow(ItemAttribute[type].Name);
}

Rml::String FormattedAmount(uint32_t amount)
{
    wchar_t text[32] = {};
    ConvertGold(static_cast<double>(amount), text);
    return StringUtils::WideToNarrow(text);
}

const JewelBank::Entry* EntryAt(int index)
{
    const auto& entries = JewelBank::Received().entries;
    if (index < 0 || index >= static_cast<int>(entries.size()))
    {
        return nullptr;
    }

    return &entries[static_cast<size_t>(index)];
}
} // namespace

CJewelBankWindow::~CJewelBankWindow()
{
    Release();
}

bool CJewelBankWindow::Create(CManager* pNewUIMng)
{
    if (pNewUIMng == nullptr)
    {
        return false;
    }

    m_pNewUIMng = pNewUIMng;
    m_pNewUIMng->AddUIObj(INTERFACE_JEWEL_BANK, this);
    m_RmlView.Ensure();
    Show(false);
    return true;
}

void CJewelBankWindow::Release()
{
    if (m_pNewUIMng)
    {
        m_pNewUIMng->RemoveUIObj(this);
        m_pNewUIMng = nullptr;
    }

    m_RmlView.Release();
}

bool CJewelBankWindow::UpdateMouseEvent()
{
    return !UI::RmlBridge::IsPointerOver(m_RmlView.Document());
}

bool CJewelBankWindow::UpdateKeyEvent()
{
    if (!g_pNewUISystem->IsVisible(INTERFACE_JEWEL_BANK) || !IsPress(VK_ESCAPE))
    {
        return true;
    }

    g_pNewUISystem->Hide(INTERFACE_JEWEL_BANK);
    PlayBuffer(SOUND_CLICK01);
    return false;
}

bool CJewelBankWindow::Update()
{
    // The server's /banco asks to open the window, also while it's hidden.
    if (JewelBank::Received().TakeOpenRequest() && !IsVisible())
    {
        g_pNewUISystem->Show(INTERFACE_JEWEL_BANK);
    }

    // The bank deposits from and withdraws into the inventory, so it closes with it.
    if (IsVisible() && !g_pNewUISystem->IsVisible(INTERFACE_INVENTORY))
    {
        g_pNewUISystem->Hide(INTERFACE_JEWEL_BANK);
    }

    SyncRmlModel();
    HandlePendingAction();
    return true;
}

bool CJewelBankWindow::Render()
{
    // Nothing native: the frame, the rows and the buttons are RmlUi. Kept because CObject requires the override.
    return true;
}

float CJewelBankWindow::GetLayerDepth()
{
    return LayerDepth;
}

void CJewelBankWindow::OpeningProcess()
{
    g_pNewUISystem->Show(INTERFACE_INVENTORY);
    m_PendingAction = Action::None;
    SocketClient->ToGameServer()->SendJewelBankStateRequest();
}

void CJewelBankWindow::ClosingProcess()
{
    m_PendingAction = Action::None;
}

void CJewelBankWindow::BindRmlModel(Rml::DataModelConstructor& c, JewelBankRmlModel& model)
{
    UI::RmlBridge::BindWindowClose(c, INTERFACE_JEWEL_BANK);
    c.Bind("text_px", &model.textPx);
    c.Bind("bold_text_px", &model.boldTextPx);
    c.Bind("title", &model.title);
    c.Bind("hint", &model.hint);
    c.Bind("deposit_text", &model.depositText);
    c.Bind("withdraw_text", &model.withdrawText);
    c.Bind("deposit_all_text", &model.depositAllText);
    c.Bind("unavailable_text", &model.unavailableText);
    c.Bind("available", &model.available);

    auto row = c.RegisterStruct<JewelBankRow>();
    row.RegisterMember("index", &JewelBankRow::index);
    row.RegisterMember("name", &JewelBankRow::name);
    row.RegisterMember("amount", &JewelBankRow::amount);
    row.RegisterMember("stored", &JewelBankRow::stored);
    c.RegisterArray<std::vector<JewelBankRow>>();
    c.Bind("rows", &model.rows);

    const auto queue = [this](Action action)
    {
        return [this, action](Rml::DataModelHandle, Rml::Event&, const Rml::VariantList& arguments)
        {
            m_PendingAction = action;
            m_PendingIndex = arguments.empty() ? -1 : arguments[0].Get<int>(-1);
        };
    };
    c.BindEventCallback("jewel_deposit", queue(Action::Deposit));
    c.BindEventCallback("jewel_withdraw", queue(Action::Withdraw));
    c.BindEventCallback("jewel_deposit_all", queue(Action::DepositAll));

    model.title = StringUtils::WideToNarrow(I18N::Game::JewelBank);
    model.hint = StringUtils::WideToNarrow(I18N::Game::SharedByAllCharactersOfTheAccount);
    model.depositText = StringUtils::WideToNarrow(I18N::Game::Deposit);
    model.withdrawText = StringUtils::WideToNarrow(I18N::Game::Withdraw);
    model.depositAllText = StringUtils::WideToNarrow(I18N::Game::DepositAll);
    model.unavailableText = StringUtils::WideToNarrow(I18N::Game::TheJewelBankIsNotAvailableOnThisServer);
    m_ShownRevision = 0;
}

void CJewelBankWindow::SyncRmlModel()
{
    m_RmlView.Ensure();
    if (!m_RmlView.Document())
    {
        return;
    }

    UI::RmlBridge::SyncDocumentVisibilityInFront(m_RmlView.Document(), IsVisible());
    if (!IsVisible())
    {
        return;
    }

    UI::RmlBridge::SyncNativeTextSize(m_RmlView.Binder());
    SyncField(m_RmlView.Binder(), &JewelBankRmlModel::boldTextPx, "bold_text_px",
              UI::RmlBridge::NativeTextPx(UI::Scaling::FontRole::Bold));
    SyncRows();
}

void CJewelBankWindow::SyncRows()
{
    const JewelBank::Store& received = JewelBank::Received();
    if (received.revision == m_ShownRevision)
    {
        return;
    }

    m_ShownRevision = received.revision;
    std::vector<JewelBankRow> rows;
    rows.reserve(received.entries.size());
    for (size_t i = 0; i < received.entries.size(); ++i)
    {
        const JewelBank::Entry& entry = received.entries[i];
        rows.push_back({static_cast<int>(i), JewelName(entry), FormattedAmount(entry.amount), entry.amount > 0});
    }

    JewelBankRmlModel& model = m_RmlView.GetModel();
    const bool available = received.known && !rows.empty();
    if (model.available != available)
    {
        model.available = available;
        m_RmlView.MarkDirty("available");
    }

    if (model.rows != rows)
    {
        model.rows = std::move(rows);
        m_RmlView.MarkDirty("rows");
    }
}

void CJewelBankWindow::HandlePendingAction()
{
    const Action action = std::exchange(m_PendingAction, Action::None);
    if (action == Action::None || !IsVisible())
    {
        return;
    }

    if (action == Action::DepositAll)
    {
        SocketClient->ToGameServer()->SendJewelBankDepositAllRequest();
        return;
    }

    const JewelBank::Entry* entry = EntryAt(m_PendingIndex);
    if (entry == nullptr)
    {
        return;
    }

    if (action == Action::Deposit)
    {
        SocketClient->ToGameServer()->SendJewelBankDepositRequest(entry->itemGroup, entry->itemNumber);
    }
    else if (entry->amount > 0)
    {
        ShowWithdrawDialog(m_PendingIndex);
    }
}

void CJewelBankWindow::ShowWithdrawDialog(int index)
{
    const JewelBank::Entry* entry = EntryAt(index);
    if (entry == nullptr || g_pGenericConfirmDialog == nullptr)
    {
        return;
    }

    // The dialog's callbacks run later, when the received state may have changed: they look the jewel up
    // again by its item instead of keeping a pointer into the entries.
    const uint8_t itemGroup = entry->itemGroup;
    const uint16_t itemNumber = entry->itemNumber;
    const auto currentEntry = [itemGroup, itemNumber]() -> const JewelBank::Entry*
    {
        for (const JewelBank::Entry& candidate : JewelBank::Received().entries)
        {
            if (candidate.itemGroup == itemGroup && candidate.itemNumber == itemNumber)
            {
                return &candidate;
            }
        }

        return nullptr;
    };

    GenericDialogConfig cfg;
    cfg.showCancel = true;
    cfg.title = StringUtils::NarrowToWide(JewelName(*entry));
    cfg.lines = {{I18N::Game::EnterTheAmountOfJewelsYouWouldLikeToWithdraw, false}};
    cfg.input = GenericDialogConfig::InputField{};
    cfg.input->mode = GenericDialogConfig::InputField::Mode::Text;
    cfg.input->maxLength = AmountFieldDigits;
    cfg.input->numericOnly = true;
    cfg.input->maxValue = [currentEntry]() -> std::uint64_t
    {
        const JewelBank::Entry* current = currentEntry();
        return current != nullptr ? JewelBank::MaxWithdrawal(*current) : 0;
    };
    cfg.onPrimary = [currentEntry, itemGroup, itemNumber]
    {
        const std::wstring text = g_pGenericConfirmDialog->GetInputText();
        const uint32_t amount = JewelBank::ParseAmount(text.c_str());
        const JewelBank::Entry* current = currentEntry();
        if (amount == 0 || current == nullptr || amount > JewelBank::MaxWithdrawal(*current))
        {
            g_pGenericConfirmDialog->KeepOpen();
            return;
        }

        SocketClient->ToGameServer()->SendJewelBankWithdrawRequest(itemGroup, itemNumber, amount);
    };
    g_pGenericConfirmDialog->Show(std::move(cfg));
}
