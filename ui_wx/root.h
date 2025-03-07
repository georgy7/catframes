#ifndef ROOT_H
#define ROOT_H

#include <wx/wx.h>

namespace cat {
namespace ui {
namespace wx {

class RootFrame : public wxFrame {
 private:
  struct impl;
  std::unique_ptr<impl> p_impl_;

 public:
  RootFrame();
  ~RootFrame();

  DECLARE_EVENT_TABLE()
};

}  // namespace wx
}  // namespace ui
}  // namespace cat

#endif
