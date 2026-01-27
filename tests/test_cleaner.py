from websense.cleaner import Cleaner


class TestCleaner:
    def test_to_text_removes_tags(self):
        html = "<div><p>Hello <b>World</b></p></div>"
        cleaned = Cleaner.to_text(html)
        assert cleaned == "Hello\nWorld"

    def test_to_text_removes_noise(self):
        html = """
        <html>
            <body>
                <script>console.log('remove me');</script>
                <style>.css { color: red; }</style>
                <nav>Menu</nav>
                <p>Content</p>
                <footer>Footer</footer>
            </body>
        </html>
        """
        cleaned = Cleaner.to_text(html)
        assert cleaned == "Content"

    def test_to_text_handles_empty(self):
        assert Cleaner.to_text("") == ""

    def test_to_text_handles_whitespace(self):
        html = "   \n\t   "
        assert Cleaner.to_text(html) == ""

    def test_to_text_handles_nested_structure(self):
        html = """
        <div>
            <h1>Header</h1>
            <section>
                <p>Paragraph 1</p>
                <br>
                <p>Paragraph 2</p>
            </section>
        </div>
        """
        cleaned = Cleaner.to_text(html)
        expected = "Header\nParagraph 1\nParagraph 2"
        assert cleaned == expected
