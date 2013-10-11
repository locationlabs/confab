from confab.merge import append, prepend, unique_union, rotate


appended = append('environment')

prepended = prepend('environment')

unique = unique_union('default')

rotated = rotate(lambda: 'pivot', ['itemA', 'pivot', 'itemB'])
