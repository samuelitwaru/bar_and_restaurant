from Application import app


@app.template_filter()
def comma_separator(value):
	if isinstance(value, int):
		return f'{value:,}'
	return value

