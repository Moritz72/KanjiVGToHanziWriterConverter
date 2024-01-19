from svgpathtools import svg2paths, CubicBezier


def transform_point(point, shift: tuple[float, float] = (0., 0.), scale: tuple[float, float] = (0., 0.)):
    return round(point.real * scale[0] + shift[0]) + round(point.imag * scale[1] + shift[1]) * 1j


def transform_path(path, shift: tuple[float, float] = (0., 0.), scale: tuple[float, float] = (1., 1.)):
    for part in path:
        part.start = transform_point(part.start, shift, scale)
        part.end = transform_point(part.end, shift, scale)
        if isinstance(part, CubicBezier):
            part.control1 = transform_point(part.control1, shift, scale)
            part.control2 = transform_point(part.control2, shift, scale)
    return path


def get_transformed_paths(
        file: str, shift: tuple[float, float] = (0., 0.), scale: tuple[float, float] = (1., 1.)
) -> list[str]:
    paths, _ = svg2paths(file)
    paths = [transform_path(path, shift, scale) for path in paths]
    return [path.d() for path in paths]


def estimate_medians(
        file: str, shift: tuple[float, float] = (0., 0.), scale: tuple[float, float] = (1., 1.), resolution: int = 5
) -> list[list[list[int]]]:
    medians = []
    paths, _ = svg2paths(file)
    for path in paths:
        points = (path.point(i / (resolution - 1)) for i in range(resolution))
        medians.append([[
            round(point.real * scale[0] + shift[0]),
            round(point.imag * scale[1] + shift[1])
        ] for point in points])
    return medians


def get_strokes_and_medians(file: str, resolution: int = 5) -> dict:
    """
    Transforms SVG data from KanjiVG to HanziWriter format and then calculates the corresponding stroke and median data.

    Parameters:
    - file (str): The path to the SVG file from KanjiVG.
    - resolution (int, optional): The resolution used in calculating the median data.
      A higher resolution results in more detailed medians. Default value is 5.

    Returns:
    - dict: A dictionary containing two keys:
        - 'strokes': A list of transformed stroke paths, formatted for HanziWriter.
        - 'medians': The estimated median data for each stroke, calculated based on the specified resolution.

    Example:
    >>> svg_data = get_strokes_and_medians("kanji.svg")
    >>> svg_data['strokes']  # List of stroke data
    >>> svg_data['medians']  # Median information for each stroke
    """
    return {
        "strokes": [v.replace(".0", "") for v in get_transformed_paths(file, (0., 900.), (1024 / 109, -1024 / 109))],
        "medians": estimate_medians(file, (0., 900.), (1024 / 109, -1024 / 109), resolution)
    }
