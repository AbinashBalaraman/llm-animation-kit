# Dependency provenance

Runtime dependencies are installed separately: Pillow (HPND-style project license), jsonschema (MIT), imageio-ffmpeg (BSD-2-Clause wrapper). FFmpeg licensing depends on the exact binary build; imageio-ffmpeg's bundled FFmpeg is separate from the wrapper license. No binary is copied into this project's distribution. Installed wheel files retain their original notices.

The local verification used Python 3.13.1, Pillow 11.3.0 and imageio-ffmpeg's FFmpeg 4.2.2 executable; the executable advertised a GPL-enabled build. It is an existing local runtime, not a recommended current release or a redistributed binary. `doctor` reports the actual runtime on each host. Use the original component/license sources when distributing dependencies:

- https://github.com/python-pillow/Pillow/blob/main/LICENSE
- https://github.com/python-jsonschema/jsonschema/blob/main/COPYING
- https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE
- https://ffmpeg.org/legal.html

Code and original procedural artwork are provided separately: runtime source GPL-3.0-or-later, authored artwork/example scenes CC0-1.0. User-imported material retains its own terms.

Version 0.2.0 bundles Lilita One and Nunito Sans font files from the Google Fonts repository, each under SIL Open Font License 1.1. Their complete original copyright/license notices accompany the files in `animation_kit/data/fonts/`. Sources: [Lilita One](https://github.com/google/fonts/tree/main/ofl/lilitaone), [Nunito Sans](https://github.com/google/fonts/tree/main/ofl/nunitosans). Font files are not covered by the project's artwork dedication.
