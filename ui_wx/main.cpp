#include <wx/wx.h>
#include "new.h"

class wxMiniApp : public wxApp {
 public:
  virtual bool OnInit();
};

IMPLEMENT_APP(wxMiniApp);

constexpr int kTestButtonId = 66345234;

class TestWindow : public wxFrame {
 public:
  TestWindow();
  ~TestWindow();

  void onCommandEvent(wxCommandEvent& evt);

  DECLARE_EVENT_TABLE()
};

BEGIN_EVENT_TABLE(TestWindow, wxFrame)
EVT_BUTTON(kTestButtonId, TestWindow::onCommandEvent)
END_EVENT_TABLE()

TestWindow::TestWindow()
    : wxFrame(NULL, wxID_ANY, "Test", wxDefaultPosition, wxDefaultSize, wxDEFAULT_FRAME_STYLE) {
  wxBoxSizer* sizer = new wxBoxSizer(wxHORIZONTAL);
  sizer->Add(new wxButton(this, kTestButtonId, "Make a window"), 1, wxEXPAND);
  this->SetSizer(sizer);
  this->SetAutoLayout(true);
}

TestWindow::~TestWindow() {}

void TestWindow::onCommandEvent(wxCommandEvent& evt) {
  cat::ui::wx::NewTaskFrame* frame = new cat::ui::wx::NewTaskFrame(this);
  frame->Show();
}

bool wxMiniApp::OnInit() {
  wxImage::AddHandler(new wxPNGHandler);
  wxImage::AddHandler(new wxJPEGHandler);

  TestWindow* frame = new TestWindow();
  SetTopWindow(frame);
  frame->Show();

  return true;
}
