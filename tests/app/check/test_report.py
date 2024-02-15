from app.check.report import CheckReport


def test_rendering_a_successful_report():
    report = CheckReport(True, 'Report Title', [])

    output = report.render()

    assert "<strong>Report Title</strong>\n\n" == output


def test_rendering_an_unsuccessful_report():
    report = CheckReport(False, 'Report Title', [
        'Something went wrong!',
        'And something else went wrong!',
    ])

    output = report.render()

    assert '<strong>Report Title</strong>' in output
    assert 'Something went wrong!' in output
    assert 'And something else went wrong!' in output
