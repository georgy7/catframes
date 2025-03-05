#ifndef UTIL_H
#define UTIL_H

#include <wx/toplevel.h>

namespace cat {
namespace ui {
namespace wx {

std::optional<wxTopLevelWindow*> GetTopLevel(wxWindow* widget);
bool IsVisible(wxTopLevelWindow* frame);

}  // namespace wx
}  // namespace ui
}  // namespace cat

#endif
