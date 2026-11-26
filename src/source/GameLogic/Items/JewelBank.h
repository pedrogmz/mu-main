#pragma once

#include <cstdint>
#include <optional>
#include <vector>

namespace GameLogic::Items::JewelBank
{
// A jewel which the server's jewel bank accepts, with the number of single jewels the account has
// stored. A bundle counts as the jewels it holds.
struct Entry
{
    uint8_t itemGroup = 0;
    uint16_t itemNumber = 0;
    uint32_t amount = 0;

    bool operator==(const Entry&) const = default;
};

// The jewel bank state which the server sends (JewelBankStateExtended, C2 F5 0F). Only OpenMU sends
// it, to the open source client, when the jewel bank feature is active on the server.
struct State
{
    // The server asks the client to open its jewel bank window (the /banco chat command).
    bool openWindow = false;
    // Every accepted jewel, in the order of the server's configuration, also when none is stored.
    std::vector<Entry> entries;
};

// Reads a JewelBankStateExtended message. Returns nothing if the message is shorter than its count
// of entries says.
std::optional<State> ReadState(const uint8_t* data, int32_t size);

// The most recent state of the server. `revision` grows with every received state, so a window
// sees that its copy is out of date.
struct Store
{
    std::vector<Entry> entries;
    uint32_t revision = 0;
    // Set when a received state asked to open the window; the window takes it.
    bool openRequested = false;
    // Set when the server sent any state at all: before that, the feature isn't known to be active.
    bool known = false;

    void Apply(State state);
    // Forgets the state, e.g. when the connection to the game server ends.
    void Reset();
    // Returns whether a received state asked to open the window, and clears the request.
    bool TakeOpenRequest();
};

Store& Received();

// The largest amount a withdrawal of the entry can ask for: what is stored, capped to what a
// withdraw request carries.
uint32_t MaxWithdrawal(const Entry& entry);

// Reads a typed amount of jewels: digits only, at least 1. Returns 0 for anything else, or when the
// amount doesn't fit the withdraw request.
uint32_t ParseAmount(const wchar_t* text);
} // namespace GameLogic::Items::JewelBank
