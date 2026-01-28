from websense.cleaner import Cleaner


class TestCleaner:
    def test_init_default_noise(self):
        cleaner = Cleaner()
        assert cleaner.noise == Cleaner.NOISE

    def test_init_custom_noise(self):
        custom_noise = {"div", "span"}
        cleaner = Cleaner(noisy_elements=custom_noise)
        assert cleaner.noise == custom_noise

    def test_init_empty_noise_uses_default(self):
        cleaner = Cleaner(noisy_elements=[])
        assert cleaner.noise == Cleaner.NOISE

    def test_preprocess_removes_noise(self):
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
        cleaner = Cleaner()
        soup = cleaner.preprocess(html)
        text = soup.get_text(separator=" ").strip()
        assert "Content" in text
        assert "Menu" not in text
        assert "Footer" not in text

    def test_preprocess_with_custom_noise(self):
        html = "<div>Remove</div><span>Keep</span>"
        cleaner = Cleaner(noisy_elements={"div"})
        soup = cleaner.preprocess(html)
        text = soup.get_text().strip()
        assert "Remove" not in text
        assert "Keep" in text

    def test_to_text_removes_tags(self):
        html = "<div><p>Hello <b>World</b></p></div>"
        cleaner = Cleaner()
        cleaned = cleaner.to_text(html)
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
        cleaner = Cleaner()
        cleaned = cleaner.to_text(html)
        assert cleaned == "Content"

    def test_to_text_handles_empty(self):
        cleaner = Cleaner()
        assert cleaner.to_text("") == ""

    def test_to_text_handles_whitespace(self):
        html = "   \n\t   "
        cleaner = Cleaner()
        assert cleaner.to_text(html) == ""

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
        cleaner = Cleaner()
        cleaned = cleaner.to_text(html)
        expected = "Header\nParagraph 1\nParagraph 2"
        assert cleaned == expected

    def test_to_markdown_basic(self):
        html = "<h1>Title</h1><p>Paragraph</p>"
        cleaner = Cleaner()
        result = cleaner.to_markdown(html)
        assert "# Title" in result
        assert "Paragraph" in result

    def test_to_markdown_removes_noise(self):
        html = """
        <html>
            <body>
                <script>console.log('remove');</script>
                <h1>Title</h1>
                <nav>Menu</nav>
            </body>
        </html>
        """
        cleaner = Cleaner()
        result = cleaner.to_markdown(html)
        assert "# Title" in result
        assert "Menu" not in result
        assert "console" not in result

    def test_to_markdown_with_links(self):
        html = '<p>Visit <a href="https://example.com">Example</a></p>'
        cleaner = Cleaner()
        result = cleaner.to_markdown(html)
        assert "[Example](https://example.com)" in result

    def test_to_markdown_handles_empty(self):
        cleaner = Cleaner()
        result = cleaner.to_markdown("")
        assert result.strip() == ""
