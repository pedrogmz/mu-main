#pragma once

#include <RmlUi/Core/Types.h>

#include <vector>

namespace mu::ui::window
{
// One jewel of the jewel bank: its name, its stored amount and whether it can be withdrawn.
struct JewelBankRow
{
    int index = 0; // into the received entries, which the buttons name
    Rml::String name;
    Rml::String amount; // with thousands separators
    bool stored = false;

    bool operator==(const JewelBankRow&) const = default;
};

struct JewelBankRmlModel
{
    float textPx = 0.f;     // native normal text size in physical px (RmlNativeTextSize.h)
    float boldTextPx = 0.f; // native bold text size

    Rml::String title;
    Rml::String hint;
    Rml::String depositText;
    Rml::String withdrawText;
    Rml::String depositAllText;
    Rml::String unavailableText;
    // No state from the server yet, or a server without the jewel bank: the hint replaces the rows.
    bool available = false;
    std::vector<JewelBankRow> rows;
};
} // namespace mu::ui::window
