#include "root.h"

namespace cat {
namespace ui {
namespace wx {

constexpr auto kALotOfMemory = 1024 * 1024 * 1024;

BEGIN_EVENT_TABLE(RootFrame, wxFrame)
END_EVENT_TABLE()

struct RootFrame::impl {
  const bool high_end_ = wxGetFreeMemory() >= kALotOfMemory;
};

RootFrame::RootFrame()
    : wxFrame(NULL, wxID_ANY, "Catframes", wxDefaultPosition, wxDefaultSize, wxDEFAULT_FRAME_STYLE),
      p_impl_{std::make_unique<impl>()} {
  wxImage::AddHandler(new wxPNGHandler);
  wxImage::AddHandler(new wxJPEGHandler);
}

RootFrame::~RootFrame() {}

// ...............................

class EntryPoint : public wxApp {
 public:
  virtual bool OnInit();
};

IMPLEMENT_APP(EntryPoint);

bool EntryPoint::OnInit() {
  SetTopWindow(new RootFrame());
  GetTopWindow()->Show();
  return true;
}

}  // namespace wx
}  // namespace ui
}  // namespace cat
