#include "carousel.h"

#include <wx/rawbmp.h>
#include "util.h"

#ifdef __WXMAC__
#include "OpenGL/gl.h"
#else
#include <GL/gl.h>
#include <GL/glext.h>
#endif

namespace cat {
namespace ui {
namespace wx {

constexpr int kCarouselTimerId = 181708047;

BEGIN_EVENT_TABLE(Carousel, wxGLCanvas)
EVT_PAINT(Carousel::onPaint)
EVT_TIMER(kCarouselTimerId, Carousel::onTimer)
END_EVENT_TABLE()

struct Texture {
  GLuint id;
  GLfloat width, height;
};

struct Carousel::impl {
  Carousel* carousel_;
  CarouselState state_ = CarouselState::kEmpty;
  std::vector<Texture> textures_;
  std::unique_ptr<wxTimer> timer_;
  std::unique_ptr<wxGLContext> m_context_;
  GLclampf r_ = 0.0f, g_ = 0.0f, b_ = 0.0f;

  std::chrono::time_point<std::chrono::steady_clock> start_time_ = std::chrono::steady_clock::now();
  unsigned int timer_counter_ = 1;
  bool visible_ = true;

  impl(Carousel* carousel) {
    carousel_ = carousel;
    timer_ = std::make_unique<wxTimer>(carousel, kCarouselTimerId);
    m_context_ = std::make_unique<wxGLContext>(carousel);
    timer_->Start(10);
  }

  void draw_image_contain(Texture texture, GLfloat alpha, float client_aspect) {
    glBindTexture(GL_TEXTURE_2D, texture.id);

    glColor4f(1.0f, 1.0f, 1.0f, alpha);

    glBegin(GL_QUADS);
    GLfloat img_width = 1.0f;
    GLfloat img_height = 1.0f;

    const float texture_aspect = texture.width / texture.height;

    if (texture_aspect >= client_aspect) {
      img_height = 1.0 / texture_aspect * client_aspect;
    } else {
      img_width = texture_aspect * (1.0f / client_aspect);
    }

    const GLfloat img_x = (1.0f - img_width) * 0.5f;
    const GLfloat img_y = (1.0f - img_height) * 0.5f;

    glTexCoord2f(0.0f, 0.0f);
    glVertex2f(img_x, img_y);

    glTexCoord2f(texture.width, 0.0f);
    glVertex2f(img_x + img_width, img_y);

    glTexCoord2f(texture.width, texture.height);
    glVertex2f(img_x + img_width, img_y + img_height);

    glTexCoord2f(0.0f, texture.height);
    glVertex2f(img_x, img_y + img_height);
    glEnd();
  }

  void render() {
    carousel_->SetCurrent(*m_context_);

    glClearColor(r_, g_, b_, 1.0f);
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_COLOR_MATERIAL);
    glEnable(GL_BLEND);
    glDisable(GL_DEPTH_TEST);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    const int client_width = carousel_->GetClientSize().GetWidth();
    const int client_height = carousel_->GetClientSize().GetHeight();
    const float client_aspect = (float)client_width / (float)client_height;

    glViewport(0, 0, client_width, client_height);

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();

    if (CarouselState::kActive == state_) {
      // Here the center of the screen is at (0, 0).
      // And the coordinates (-1, -1) indicate the lower-left corner.
      // It is more convenient for me to have the point (0, 0) in the
      // upper-left corner, and the (1, 1) in the lower-right corner.

      // To rotate 180 degrees relative to the X-axis
      // is the same as to reflect vertically.
      glRotatef(180.0f, 1.0f, 0.0f, 0.0f);
      glTranslatef(-1.0f, -1.0f, 0.0f);
      glScalef(2.0f, 2.0f, 2.0f);

      const int images_len = (int)textures_.size();

      const auto now_time = std::chrono::steady_clock::now();
      const std::chrono::duration<double> seconds_since_start = now_time - start_time_;

      const double t = (images_len > 0) ? fmod(seconds_since_start.count(), 2 * images_len) : 0.0;

      for (int i = 0; i < images_len; i++) {
        if ((2 * i <= t) && (t < 2 * i + 1)) {
          draw_image_contain(textures_.at(i), 1.0f, client_aspect);
        } else if ((2 * i + 1 <= t) && (t < 2 * i + 2)) {
          const Texture this_image = textures_.at(i);
          const Texture next_image = textures_.at((i + 1) % images_len);
          const double transition = (t - (2 * i + 1));
          draw_image_contain(this_image, 1.0f - transition, client_aspect);
          draw_image_contain(next_image, transition, client_aspect);
        }
      }
    }

    glFlush();
    carousel_->SwapBuffers();
  }
};

Carousel::Carousel(wxWindow* parent, int* args)
    : wxGLCanvas(parent,
                 wxID_ANY,
                 args,
                 wxDefaultPosition,
                 wxDefaultSize,
                 wxFULL_REPAINT_ON_RESIZE),
      p_impl_{std::make_unique<impl>(this)} {}

Carousel::~Carousel() {}

void Carousel::setState(CarouselState state) {
  p_impl_->state_ = state;
}

void Carousel::setBackground(unsigned char r, unsigned char g, unsigned char b) {
  p_impl_->r_ = (GLclampf)r / 255.0f;
  p_impl_->g_ = (GLclampf)g / 255.0f;
  p_impl_->b_ = (GLclampf)b / 255.0f;
}

// Pass non-empty prefix to log errors.
bool clear_gl_errors(const wxString& log_message_prefix) {
  bool had_errors = false;
  for (GLenum error = glGetError(); GL_NO_ERROR != error; error = glGetError()) {
    had_errors = true;
    if (!log_message_prefix.IsEmpty()) {
      wxLogError(wxString::Format("%s: %d", log_message_prefix, error));
    }
  }
  return had_errors;
}

void copy_rgb1(wxImage& source, const int destination_width, GLubyte* const destination) {
  assert(!source.HasAlpha());

  const int source_width = source.GetWidth();
  const int source_height = source.GetHeight();

  assert(source_width <= destination_width);
  assert(source_height <= destination_width);

  GLubyte* const rgb_data = source.GetData();

  const std::size_t src_line = 3 * source_width;
  const std::size_t dst_line = 4 * destination_width;

  std::size_t src_index = 0;

  for (int y = 0; y < source_height; y++) {
    std::size_t dst_index = dst_line * y;

    const std::size_t next_line = src_index + src_line;
    for (; src_index < next_line; src_index += 3, dst_index += 4) {
      destination[dst_index + 0] = rgb_data[src_index + 0];
      destination[dst_index + 1] = rgb_data[src_index + 1];
      destination[dst_index + 2] = rgb_data[src_index + 2];
      destination[dst_index + 3] = 255;
    }
  }
}

void copy_rgba(wxImage& source, const int destination_width, GLubyte* const destination) {
  assert(source.HasAlpha());

  const int source_width = source.GetWidth();
  const int source_height = source.GetHeight();

  assert(source_width <= destination_width);
  assert(source_height <= destination_width);

  GLubyte* const rgb_data = source.GetData();
  GLubyte* const alpha = source.GetAlpha();

  const std::size_t dst_line = 4 * destination_width;

  std::size_t src_pixel = 0;

  for (int y = 0; y < source_height; y++) {
    std::size_t dst_index = dst_line * y;

    const std::size_t next_line = src_pixel + source_width;
    for (; src_pixel < next_line; src_pixel++, dst_index += 4) {
      std::size_t src_rgb_index = 3 * src_pixel;
      destination[dst_index + 0] = rgb_data[src_rgb_index + 0];
      destination[dst_index + 1] = rgb_data[src_rgb_index + 1];
      destination[dst_index + 2] = rgb_data[src_rgb_index + 2];
      destination[dst_index + 3] = alpha[src_pixel];
    }
  }
}

uint32_t Carousel::add(wxImage& image) {
  assert(image.IsOk());

  std::chrono::time_point<std::chrono::steady_clock> start = std::chrono::steady_clock::now();

  wxClientDC dc(this);
  wxGLCanvas::SetCurrent(*(p_impl_->m_context_));

  Texture result;

  constexpr GLint large_size = 2048;

  GLint max_size;
  clear_gl_errors("");
  glGetIntegerv(GL_MAX_TEXTURE_SIZE, &max_size);
  if (clear_gl_errors("Could not get GL_MAX_TEXTURE_SIZE")) {
    max_size = 256;
  }

  max_size = std::min(large_size, max_size);

  const int goal_size =
      std::min(max_size, 1 << (int)lround(ceil(log2(fmax(image.GetWidth(), image.GetHeight())))));

  const bool should_zoom_out = (image.GetWidth() > goal_size) || (image.GetHeight() > goal_size);

  if (should_zoom_out) {
    const double scale = double(image.GetWidth()) / double(image.GetHeight()) >= 1.0
                             ? double(goal_size) / double(image.GetWidth())
                             : double(goal_size) / double(image.GetHeight());

    image.Rescale((int)lround(scale * image.GetWidth()), (int)lround(scale * image.GetHeight()),
                  wxIMAGE_QUALITY_HIGH);
  }

  result.width = (GLfloat)image.GetWidth() / (GLfloat)goal_size;
  result.height = (GLfloat)image.GetHeight() / (GLfloat)goal_size;

  constexpr int bytesPerPixel = 4;
  GLubyte* const pixels = new GLubyte[bytesPerPixel * goal_size * goal_size];

  if (image.HasAlpha()) {
    copy_rgba(image, goal_size, pixels);
  } else {
    copy_rgb1(image, goal_size, pixels);
  }

  glGenTextures(1, &result.id);
  glBindTexture(GL_TEXTURE_2D, result.id);

  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);

  const GLint border = 0;
  const GLint internal_format = GL_COMPRESSED_RGBA;
  const GLint pixel_data_format = GL_RGBA;

  clear_gl_errors("");
  glTexImage2D(GL_TEXTURE_2D, 0, internal_format, goal_size, goal_size, border, pixel_data_format,
               GL_UNSIGNED_BYTE, pixels);

  // Fallback
  if (clear_gl_errors("")) {
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, goal_size, goal_size, border, pixel_data_format,
                 GL_UNSIGNED_BYTE, pixels);
  }

  delete[] pixels;

  p_impl_->textures_.push_back(result);

  std::chrono::time_point<std::chrono::steady_clock> end = std::chrono::steady_clock::now();
  const std::chrono::duration<double> execution_time = end - start;
  wxLogMessage("Duration: %f", execution_time.count());

  return result.id;
}

void Carousel::remove(uint32_t id) {}

unsigned int Carousel::count() {
  return (unsigned int)p_impl_->textures_.size();
}

void Carousel::onPaint(wxPaintEvent& evt) {
  wxPaintDC dc(this);
  p_impl_->render();
}

void Carousel::onTimer(wxTimerEvent& WXUNUSED(event)) {
  const unsigned int counter = ++(p_impl_->timer_counter_);

  auto top_level = GetTopLevel(this);

  if (top_level.has_value()) {
    if (!top_level.value()->IsIconized()) {
      if (p_impl_->visible_) {
        wxClientDC dc(this);
        p_impl_->render();
      }

      if (counter % 60 == 0) {
        p_impl_->visible_ = IsVisible(top_level.value());
      }
    }
  }
}

}  // namespace wx
}  // namespace ui
}  // namespace cat
