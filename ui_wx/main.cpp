#include <wx/wx.h>
#include "new.h"

class wxMiniApp : public wxApp {
 public:
  virtual bool OnInit();
};

IMPLEMENT_APP(wxMiniApp);

bool wxMiniApp::OnInit() {
  wxImage::AddHandler(new wxPNGHandler);
  wxImage::AddHandler(new wxJPEGHandler);

  cat::ui::wx::NewTaskFrame* frame = new cat::ui::wx::NewTaskFrame();
  SetTopWindow(frame);
  frame->Show();

  return true;
}
