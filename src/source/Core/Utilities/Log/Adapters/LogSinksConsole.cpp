#include "Core/Utilities/Log/TargetLogSinks.h"

#include <spdlog/sinks/stdout_color_sinks.h>

namespace mu::log
{
// Nobody reads MuError.log in the browser: the log also goes to stdout, which Emscripten prints to the devtools console.
std::vector<spdlog::sink_ptr> TargetLogSinks()
{
    return {std::make_shared<spdlog::sinks::stdout_color_sink_mt>()};
}
} // namespace mu::log
