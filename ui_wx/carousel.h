#ifndef CAROUSEL_H
#define CAROUSEL_H

#include <wx/glcanvas.h>
#include <wx/wx.h>
#include <cstdint>

namespace cat {
namespace ui {
namespace wx {

constexpr int kCarouselTimerId = 181708047;
enum class CarouselState { kEmpty, kLoading, kActive, kStopped };

class Carousel : public wxGLCanvas {
 private:
  struct impl;
  std::unique_ptr<impl> p_impl_;

 public:
  Carousel(wxWindow* parent, int* args);
  ~Carousel();

  void setState(CarouselState state);
  void setBackground(unsigned char r, unsigned char g, unsigned char b);

  uint32_t add(wxImage& image);
  void remove(uint32_t id);
  unsigned int count();

  void onPaint(wxPaintEvent& evt);
  void onTimer(wxTimerEvent& event);

  DECLARE_EVENT_TABLE()
};

}  // namespace wx
}  // namespace ui
}  // namespace cat

#endif
