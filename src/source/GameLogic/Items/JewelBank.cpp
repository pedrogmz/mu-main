#include "GameLogic/Items/JewelBank.h"

#include <cstdint>
#include <limits>
#include <utility>

namespace GameLogic::Items::JewelBank
{
namespace
{
// Offsets of the JewelBankStateExtended message (C2 header with sub code).
constexpr int32_t OpenWindowOffset = 5;
constexpr int32_t CountOffset = 6;
constexpr int32_t EntriesOffset = 7;

// Offsets within one entry.
constexpr int32_t EntrySize = 8;
constexpr int32_t ItemGroupOffset = 0;
constexpr int32_t ItemNumberOffset = 2;
constexpr int32_t AmountOffset = 4;

// The withdraw request's amount is 32 bits; the server stores a signed 32-bit amount.
constexpr uint32_t MaxRequestAmount = static_cast<uint32_t>(std::numeric_limits<int32_t>::max());
constexpr uint32_t DecimalBase = 10;

uint16_t ReadUInt16LittleEndian(const uint8_t* data)
{
    return static_cast<uint16_t>(data[0] | (data[1] << 8));
}

uint32_t ReadUInt32LittleEndian(const uint8_t* data)
{
    return static_cast<uint32_t>(data[0]) | (static_cast<uint32_t>(data[1]) << 8) |
           (static_cast<uint32_t>(data[2]) << 16) | (static_cast<uint32_t>(data[3]) << 24);
}
} // namespace

std::optional<State> ReadState(const uint8_t* data, int32_t size)
{
    if (data == nullptr || size < EntriesOffset)
    {
        return std::nullopt;
    }

    const int32_t count = data[CountOffset];
    if (size < EntriesOffset + count * EntrySize)
    {
        return std::nullopt;
    }

    State state;
    state.openWindow = data[OpenWindowOffset] != 0;
    state.entries.reserve(static_cast<size_t>(count));
    for (int32_t i = 0; i < count; ++i)
    {
        const uint8_t* entry = data + EntriesOffset + i * EntrySize;
        state.entries.push_back({entry[ItemGroupOffset], ReadUInt16LittleEndian(entry + ItemNumberOffset),
                                 ReadUInt32LittleEndian(entry + AmountOffset)});
    }

    return state;
}

void Store::Apply(State state)
{
    entries = std::move(state.entries);
    openRequested = openRequested || state.openWindow;
    known = true;
    ++revision;
}

void Store::Reset()
{
    entries.clear();
    openRequested = false;
    known = false;
    ++revision;
}

bool Store::TakeOpenRequest()
{
    return std::exchange(openRequested, false);
}

Store& Received()
{
    static Store store;
    return store;
}

uint32_t MaxWithdrawal(const Entry& entry)
{
    return entry.amount < MaxRequestAmount ? entry.amount : MaxRequestAmount;
}

uint32_t ParseAmount(const wchar_t* text)
{
    if (text == nullptr || *text == L'\0')
    {
        return 0;
    }

    uint64_t amount = 0;
    for (const wchar_t* c = text; *c != L'\0'; ++c)
    {
        if (*c < L'0' || *c > L'9')
        {
            return 0;
        }

        amount = amount * DecimalBase + static_cast<uint64_t>(*c - L'0');
        if (amount > MaxRequestAmount)
        {
            return 0;
        }
    }

    return static_cast<uint32_t>(amount);
}
} // namespace GameLogic::Items::JewelBank
