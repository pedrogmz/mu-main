#include "stdafx.h"

// The HUD's top-right buttons (shop, character, inventory, friends, menu) for the web build's own
// page bar: the page draws them together with its other buttons, polls their state and forwards its
// clicks here; main_frame_top.rml hides its row meanwhile. Native builds keep the RmlUi row.
#ifdef __EMSCRIPTEN__
#include <emscripten.h>

#include "Scenes/SceneCore.h"
#include "UI/Core/WindowSystem.h"
#include "UI/HUD/MainFrameWindow.h"

namespace
{
// MuWeb_TopButtonClick()'s button numbers, in the bar's order.
enum class TopButton
{
    CashShop = 0,
    Character = 1,
    Inventory = 2,
    Friends = 3,
    Menu = 4,
};

// MuWeb_TopButtonsState()'s bits.
enum TopButtonsStateBit : int
{
    StateShown = 1 << 0,
    StateCashShopOpen = 1 << 1,
    StateCharacterOpen = 1 << 2,
    StateInventoryOpen = 1 << 3,
    StateFriendsOpen = 1 << 4,
    StateMenuOpen = 1 << 5,
    StateCharacterAlert = 1 << 6,
    StateFriendsAlert = 1 << 7,
};

mu::ui::window::CMainFrameWindow* HudInWorld()
{
    if (SceneFlag != MAIN_SCENE)
        return nullptr;
    mu::ui::window::CMainFrameWindow* frame = g_pMainFrame;
    if (frame == nullptr || !frame->IsVisible())
        return nullptr;
    return frame;
}

int Bit(bool set, TopButtonsStateBit bit)
{
    return set ? bit : 0;
}
} // namespace

extern "C" {

// The buttons' state as TopButtonsStateBit flags; 0 outside the world (no HUD to drive).
EMSCRIPTEN_KEEPALIVE
int MuWeb_TopButtonsState()
{
    const mu::ui::window::CMainFrameWindow* frame = HudInWorld();
    if (frame == nullptr)
        return 0;
    const auto state = frame->GetTopButtonsState();
    return StateShown | Bit(state.cShopOpen, StateCashShopOpen) | Bit(state.chaInfoOpen, StateCharacterOpen) |
           Bit(state.myInvenOpen, StateInventoryOpen) | Bit(state.friendOpen, StateFriendsOpen) |
           Bit(state.windowOpen, StateMenuOpen) | Bit(state.chaInfoAlert, StateCharacterAlert) |
           Bit(state.friendAlert, StateFriendsAlert);
}

// A click on one of the page's top buttons; handled on the next frame like the RmlUi row's.
EMSCRIPTEN_KEEPALIVE
void MuWeb_TopButtonClick(int button)
{
    mu::ui::window::CMainFrameWindow* frame = HudInWorld();
    if (frame == nullptr)
        return;
    switch (static_cast<TopButton>(button))
    {
    case TopButton::CashShop: frame->RmlClickCShop(); break;
    case TopButton::Character: frame->RmlClickChaInfo(); break;
    case TopButton::Inventory: frame->RmlClickMyInven(); break;
    case TopButton::Friends: frame->RmlClickFriend(); break;
    case TopButton::Menu: frame->RmlClickWindow(); break;
    }
}

// The page draws the buttons (1) or leaves them to main_frame_top.rml (0).
EMSCRIPTEN_KEEPALIVE
void MuWeb_SetTopButtonsExternal(int external)
{
    mu::ui::window::CMainFrameWindow* frame = g_pMainFrame;
    if (frame != nullptr)
        frame->SetTopButtonsExternal(external != 0);
}

} // extern "C"
#endif
