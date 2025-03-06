#include "util.h"

#include <wx/display.h>

namespace cat {
namespace ui {
namespace wx {

std::optional<wxTopLevelWindow*> GetTopLevel(wxWindow* widget) {
  if (nullptr == widget) {
    return std::nullopt;
  }

  // IsTopLevel() returns true for all descendants of the wxTopLevelWindow class,
  // even if they have a non-null pointer to a parent.

  // In general, if IsTopLevel() returns false, the parent should be there,
  // but it's better to be safe than to have spontaneous program crashes.

  wxWindow* top = widget;
  while (!(top->IsTopLevel()) && (top->GetParent() != nullptr)) {
    top = top->GetParent();
  }

  return top->IsTopLevel() ? std::optional<wxTopLevelWindow*>{dynamic_cast<wxTopLevelWindow*>(top)}
                           : std::nullopt;
}

bool IsVisible(wxTopLevelWindow* window) {
  const int display_index = wxDisplay::GetFromWindow(window);
  const wxRect window_rect = window->GetScreenRect();

  const int step = 64;
  const int header = 25;

  bool found = false;

  if (display_index != wxNOT_FOUND) {
    wxDisplay display(display_index);
    const wxRect display_rect = display.GetGeometry();

    for (int y = window_rect.GetTop() + header; y < window_rect.GetBottom(); y += step) {
      for (int x = window_rect.GetLeft(); x < window_rect.GetRight(); x += step) {
        if (!found) {
          wxPoint point(x, y);
          if (display_rect.Contains(point)) {
            const wxWindow* w = wxFindWindowAtPoint(point);
            found = w && (window == w);
          }
        }
      }
    }
  }

  return found;
}

}  // namespace wx
}  // namespace ui
}  // namespace cat