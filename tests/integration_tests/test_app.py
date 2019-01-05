import io

from main import main


input_file_path = 'tests/integration_tests/input.json'
output_file_path = 'tests/integration_tests/expected_output.json'


class TestApp:
    def test_(self):
        output_stream = io.StringIO()
        with open(input_file_path, 'r') as file_object:
            main(input_stream=file_object, output_stream=output_stream)

        output_stream.seek(0)
        output_data = output_stream.read()

        with open(output_file_path, 'r') as expected_output_file:
            expected_data = expected_output_file.read()

        assert output_data == expected_data
