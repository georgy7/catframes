#include "new.h"

#include <wx/splitter.h>
#include "carousel.h"

namespace cat {
namespace ui {
namespace wx {

constexpr int kFilePickerId = 76223984;

BEGIN_EVENT_TABLE(NewTaskFrame, wxFrame)
EVT_CLOSE(NewTaskFrame::onClose)
EVT_FILEPICKER_CHANGED(kFilePickerId, NewTaskFrame::OnPathChanged)
END_EVENT_TABLE()

constexpr int kMinSettingsWidth = 250;
constexpr long kSplitterStyle = wxSP_LIVE_UPDATE | wxSP_3D;

enum class RGBChannel { kRed, kGreen, kBlue };

struct RGBData {
  unsigned char r_ = 0, g_ = 0, b_ = 0;
};

class MySlider : public wxSlider {
 private:
  const RGBChannel channel_;
  RGBData* const color_;
  Carousel* const carousel_;

 public:
  MySlider(wxWindow* parent, RGBChannel channel, RGBData* rgb, Carousel* carousel)
      : wxSlider(parent, wxID_ANY, 0, 0, 255),
        channel_{channel},
        color_{rgb},
        carousel_{carousel} {}

  void onValueChange(wxScrollEvent& evt) {
    auto value = (unsigned char)evt.GetPosition();

    if (RGBChannel::kRed == channel_) {
      color_->r_ = value;
    } else if (RGBChannel::kGreen == channel_) {
      color_->g_ = value;
    } else if (RGBChannel::kBlue == channel_) {
      color_->b_ = value;
    }

    carousel_->setBackground(color_->r_, color_->g_, color_->b_);
  }

  DECLARE_EVENT_TABLE()
};

BEGIN_EVENT_TABLE(MySlider, wxSlider)
EVT_SCROLL_THUMBTRACK(MySlider::onValueChange)
END_EVENT_TABLE()

struct NewTaskFrame::impl {
  NewTaskFrame* frame_;
  Carousel* carousel_;
  RGBData rgb_;

  impl(NewTaskFrame* frame) {
    frame_ = frame;

    wxBoxSizer* top_sizer = new wxBoxSizer(wxHORIZONTAL);
    top_sizer->SetMinSize(wxSize(640, 400));

    wxSplitterWindow* splitter =
        new wxSplitterWindow(frame_, wxID_ANY, wxDefaultPosition, wxDefaultSize, kSplitterStyle);
    splitter->SetSashInvisible(false);
    splitter->SetMinimumPaneSize(kMinSettingsWidth);
    splitter->SetSashGravity(1.0);

    wxPanel* canvas_panel = new wxPanel(splitter, wxID_ANY);
    int args[] = {WX_GL_RGBA, WX_GL_DOUBLEBUFFER, WX_GL_DEPTH_SIZE, 16, 0};
    carousel_ = new Carousel(canvas_panel, args);
    wxBoxSizer* canvas_panel_sizer = new wxBoxSizer(wxHORIZONTAL);
    canvas_panel_sizer->Add(carousel_, 1, wxEXPAND);
    canvas_panel->SetSizer(canvas_panel_sizer);

    wxPanel* settings_panel = new wxPanel(splitter, wxID_ANY);
    wxBoxSizer* settings_sizer = new wxBoxSizer(wxVERTICAL);
    wxFlexGridSizer* color_grid = new wxFlexGridSizer(0, 2, 0, 0);

    wxFilePickerCtrl* file_picker_ctrl =
        new wxFilePickerCtrl(settings_panel, kFilePickerId, wxEmptyString,
                             wxASCII_STR(wxFileSelectorPromptStr), "PNG, JPG|*.png;*.jpg;*.jpeg",
                             wxDefaultPosition, wxDefaultSize, wxFLP_OPEN | wxFLP_FILE_MUST_EXIST);

    settings_sizer->Add(0, 10, 0, wxALL);
    settings_sizer->Add(file_picker_ctrl, 0, wxALL | wxEXPAND, 5);

    settings_sizer->Add(0, 20, 0, wxALL);
    settings_sizer->Add(new wxStaticText(settings_panel, wxID_ANY, "Color"), 0, wxALL);
    settings_sizer->Add(0, 10, 0, wxALL);
    settings_sizer->Add(color_grid, 1, wxALL | wxEXPAND);

    color_grid->SetFlexibleDirection(wxBOTH);
    color_grid->SetNonFlexibleGrowMode(wxFLEX_GROWMODE_SPECIFIED);
    color_grid->AddGrowableCol(1);

    wxStaticText* red_label = new wxStaticText(settings_panel, wxID_ANY, "R");
    wxStaticText* green_label = new wxStaticText(settings_panel, wxID_ANY, "G");
    wxStaticText* blue_label = new wxStaticText(settings_panel, wxID_ANY, "B");

    MySlider* red_slider = new MySlider(settings_panel, RGBChannel::kRed, &rgb_, carousel_);
    MySlider* green_slider = new MySlider(settings_panel, RGBChannel::kGreen, &rgb_, carousel_);
    MySlider* blue_slider = new MySlider(settings_panel, RGBChannel::kBlue, &rgb_, carousel_);

    color_grid->Add(red_label, 0, wxALL);
    color_grid->Add(red_slider, 0, wxALL | wxEXPAND);
    color_grid->Add(green_label, 0, wxALL);
    color_grid->Add(green_slider, 0, wxALL | wxEXPAND);
    color_grid->Add(blue_label, 0, wxALL);
    color_grid->Add(blue_slider, 0, wxALL | wxEXPAND);

    settings_panel->SetSizer(settings_sizer);
    splitter->SplitVertically(canvas_panel, settings_panel, -kMinSettingsWidth);
    top_sizer->Add(splitter, 1, wxEXPAND);
    frame_->SetSizerAndFit(top_sizer);
    frame_->SetAutoLayout(true);
  }
};

NewTaskFrame::NewTaskFrame(wxWindow* parent)
    : wxFrame(parent, wxID_ANY, "New task", wxDefaultPosition, wxDefaultSize, wxDEFAULT_FRAME_STYLE),
      p_impl_{std::make_unique<impl>(this)} {}

NewTaskFrame::~NewTaskFrame() {}

void NewTaskFrame::onClose(wxCloseEvent& evt) {
  evt.Skip();
}

void NewTaskFrame::OnPathChanged(wxFileDirPickerEvent& evt) {
  wxImage image;
  image.LoadFile(evt.GetPath());

  if (image.Ok()) {
    p_impl_->carousel_->setState(CarouselState::kLoading);
    p_impl_->carousel_->add(image);
    p_impl_->carousel_->setState(CarouselState::kActive);
  } else {
    wxLogError(wxString::Format("Could not load: %s", evt.GetPath()));
  }
}

}  // namespace wx
}  // namespace ui
}  // namespace cat
