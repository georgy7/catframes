# Catframes Changelog

## [2024.8.0] – 2024-08-31
### Added
- GUI application written in Tkinter. You can run it like this: `catmanager`
- System option `--live-preview` (GUI related).

### Changed
- The `WARN` overlay becomes optional. These warnings embedded in the video stream
  are quite useless for casual users who run the script manually, and whose data
  is not related to CCTV.

### Fixed
- We have eliminated network-related delays on some platforms (mostly Windows) by switching
  to pipes. Now the script writes uncompressed stream of pixels to the FFmpeg standard input.
  Thus, on some systems, the execution was accelerated three times.

### Removed
- Web server. Firewall warnings will no longer appear.

### Deprecated
- System option `--port-range`: it does not affect anything.


## [2024.4.0] – 2024-05-04
Some things in the source code have been renamed,
and some comments have been translated into English.


## [2024.3.1] – 2024-04-03
### Fixed
- WSGIServer shutdown


## [2024.3.0] – 2024-03-31
### Changed
- I preload frames in a separate thread. It's about 15 percent faster.
- Using other VP9 options results in slightly larger files, but 1.5–2 times faster.


## [2024.2.0] – 2024-02-07
### Changed
- Destination file name is allowed (and ignored) with option `--resolutions`
- No subsampling in high quality mode; moderate subsampling in medium quality mode

### Added
- Support for QOI and PCX input image formats

### Removed
- Options `--trim-start` and `--trim-end`


## [2023.9.1] – 2023-10-19
### Fixed
- A bug in the resolution resolving algorithm, leading to division by zero in the presence
  of odd frame sizes due to incorrect use of rounded (to even) size.


## [2023.9.0] – 2023-09-24
The version numbers now almost match the SemVer recommendations.

### Changed
- Video resolution resolving algorithm copes better with controversial situations.

### Added
- The ability to set the range of allowed ports (`-p min:max`).
- The ability to make videos even from empty or non-existent folders (`--sure`).

### Deprecated
- Options `--trim-start` and `--trim-end`


## [2023.5] – 2023-05-19
Not published in PYPI.

The script works in Python 3.7 again.


## [2022.10] – 2022-10-09
Not published in PYPI.

Complete re-implementation that uses a web server to pass frames to FFmpeg.
Thus, intermediate results of image processing are not saved to the disk, which reduces its wear.

### Added
- The ability to compress images not from the current folder.
- The ability to concatenate multiple folders into one video.
- A DSL named OverLang to mark up overlays.
- Result guarantee: the video will be made under any circumstances!
- Warning screens (refers to the previous item). They are embedded in the video stream.

### Changed
- It sorts files in natural order (in each folder separately).
- The text color and the background color of the text dynamically adjust to the video
  (the solid background fill is designed to make the text readable against a non-uniform background).
- Videos have black margins (black background) by default.


## Early history
[The first prototypes] developed between 2018 and 2020 used FFmpeg with [ImageMagick].

They had the following problems:

1. The program used disk to process the frames. It was slow on HDD and wore out SSD.
2. It processed the frames in-place. If something went wrong, the program could simply spoil the original data.
3. It chose the most frequent resolution, which, under special circumstances, could lower the quality of most frames.
   I added an improved resolution selection method based on the weighted average only in September 2020.
4. Its scaling heuristic was quite confusing and stupid.
5. Lexicographic file sorting is usually not what you expect.
6. Poor default settings (acid colors, one frame per second).

There was also an option to remove the original data after processing.
It make sense, probably, when compressing CCTV frames.



[ImageMagick]: https://imagemagick.org/
[The first prototypes]: https://github.com/georgy7/catframes/tree/e65eb40a6d98b72a9d6609c057254a7ede3a0959
[2022.10]: https://github.com/georgy7/catframes/tree/b919b07d7e2944aaab79181c4312aba083ffd1d9
[2023.5]: https://github.com/georgy7/catframes/tree/008297abe6e821f0aeda6a327ae8c15220995402
[2023.9.0]: https://github.com/georgy7/catframes/tree/archive/dev_2023_09
[2023.9.1]: https://github.com/georgy7/catframes/tree/v2023.9.1
[2024.2.0]: https://github.com/georgy7/catframes/tree/v2024.2.0
[2024.3.0]: https://github.com/georgy7/catframes/tree/v2024.3.0
[2024.3.1]: https://github.com/georgy7/catframes/tree/v2024.3.1
[2024.4.0]: https://github.com/georgy7/catframes/tree/v2024.4.0
[2024.8.0]: https://github.com/georgy7/catframes/tree/v2024.8.0
