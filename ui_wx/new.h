#ifndef TASK_NEW_H
#define TASK_NEW_H

#include <wx/filepicker.h>
#include <wx/wx.h>

namespace cat {
namespace ui {
namespace wx {

class NewTaskFrame : public wxFrame {
 private:
  struct impl;
  std::unique_ptr<impl> p_impl_;

 public:
  NewTaskFrame();
  ~NewTaskFrame();

  void onClose(wxCloseEvent& evt);
  void OnPathChanged(wxFileDirPickerEvent& evt);

  DECLARE_EVENT_TABLE()
};

}  // namespace wx
}  // namespace ui
}  // namespace cat

#endif
