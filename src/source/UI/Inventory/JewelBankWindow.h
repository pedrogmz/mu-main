#pragma once

#include "UI/Core/WindowObject.h"
#include "UI/Core/WindowManager.h"
#include "UI/Inventory/JewelBankRmlModel.h"
#include "UI/RmlBridge/RmlThemedView.h"

#include <cstdint>

namespace Rml
{
class ElementDocument;
}

namespace mu::ui::window
{
// The jewel bank of OpenMU (docs/jewel-bank.md): the jewels the account stored by number, docked beside
// the inventory. jewel_bank.rml draws it; C++ keeps the received state, Escape, the amount dialog and
// every request it sends. It opens with the inventory's jewel bank button or the server's /banco.
class CJewelBankWindow : public CObject
{
public:
    CJewelBankWindow() = default;
    ~CJewelBankWindow() override;

    bool Create(CManager* pNewUIMng);
    void Release();

    Rml::ElementDocument* GetFillDocument() const override { return m_RmlView.Document(); }
    Rml::ElementDocument* GetPlacedDocument() const override { return m_RmlView.Document(); }

    bool UpdateMouseEvent() override;
    bool UpdateKeyEvent() override;
    bool Update() override;
    bool Render() override;

    float GetLayerDepth() override;

    void OpeningProcess();
    void ClosingProcess();

private:
    // What a click RmlUi reported asks for; handled in Update(), outside of RmlUi's event dispatch.
    enum class Action
    {
        None,
        Deposit,
        Withdraw,
        DepositAll,
    };

    void BindRmlModel(Rml::DataModelConstructor& c, JewelBankRmlModel& model);
    void SyncRmlModel();
    void SyncRows();
    void HandlePendingAction();
    void ShowWithdrawDialog(int index);

    CManager* m_pNewUIMng = nullptr;
    Action m_PendingAction = Action::None;
    int m_PendingIndex = -1;
    uint32_t m_ShownRevision = 0;

    UI::RmlBridge::ThemedView<JewelBankRmlModel> m_RmlView{"jewel_bank",
        [this](Rml::DataModelConstructor& c, JewelBankRmlModel& model) { BindRmlModel(c, model); },
        {{"Data/Interface/RmlUi/jewel_bank.rml"}}};
};
} // namespace mu::ui::window
