from django.test import TestCase

from pecunia.templatetags.pecunia_tags import highlight_words


# Create your tests here.
class LeidenDisplayTestCase(TestCase):
    def test_lb_tag(self):
        output = highlight_words('<lb n="1" />')
        self.assertEqual("", output)
        output = highlight_words('<lb n="1" /><lb n="2" />')
        self.assertEqual("<br>", output)

    def test_orig_tag(self):
        output = highlight_words('<orig>αβ</orig>')
        self.assertEqual("ΑΒ", output)

    def test_unclear_tag(self):
        output = highlight_words('<unclear>αβ</unclear>')
        self.assertEqual("α̣β̣", output)

    def test_gap_quantity(self):
        output = highlight_words('<gap reason="illegible" quantity="3" unit="character" />')
        self.assertEqual("...", output)
        output = highlight_words('<gap reason="illegible" quantity="6" unit="character" />')
        self.assertEqual("......", output)

    def test_gap_extent(self):
        output = highlight_words('<gap reason="illegible" extent="unknown" unit="character" />')
        self.assertEqual("----", output)
        output = highlight_words('<gap reason="illegible" extent="several lines" unit="character" />')
        self.assertEqual("----", output)

    def test_gap_lost(self):
        output = highlight_words('<gap reason="lost" quantity="3" unit="character"/>')
        self.assertEqual('[...]', output)
        output = highlight_words('<gap reason="lost" quantity="6" unit="character"/>')
        self.assertEqual('[......]', output)
        output = highlight_words('<gap reason="lost" extent="unknown" unit="character" />')
        self.assertEqual("[----]", output)
        output = highlight_words('<gap reason="lost" extent="several lines" unit="character" />')
        self.assertEqual("[----]", output)

    def test_del(self):
        output = highlight_words('<del rend="erasure">αβ</del>')
        self.assertEqual("〚αβ〛", output)

    def test_del_gap(self):
        output = highlight_words('<del rend="erasure"><gap reason="lost" quantity="3" unit="character"/></del>')
        self.assertEqual('〚...〛', output)

    def test_supplied_lost(self):
        output = highlight_words('<supplied reason="lost">αβ</supplied>')
        self.assertEqual('[αβ]', output)

    def test_supplied_omitted(self):
        output = highlight_words('<supplied reason="omitted">αβ</supplied>')
        self.assertEqual('<αβ>', output)

    def test_surplus_tag(self):
        output = highlight_words('<surplus>αβ</surplus>')
        self.assertEqual('{αβ}', output)

    def test_choice_tag(self):
        output = highlight_words('<choice><corr>αβ</corr><sic>βα</sic></choice>')
        self.assertEqual('<αβ>', output)

    def test_expan_tag(self):
        output = highlight_words('<expan><abbr>α</abbr><ex>βγ</ex></expan>')
        self.assertEqual('α(βγ)', output)

    def test_expan_tag_low(self):
        output = highlight_words('<expan><abbr>α</abbr><ex cert="low">βγ</ex></expan>')
        self.assertEqual('α(βγ?)', output)

    def test_expan_tag_incomplete(self):
        output = highlight_words('<w part="I"><expan>α<ex>βγ</ex></expan></w>')
        self.assertEqual('α(βγ-)', output)

    def test_space_tag(self):
        output = highlight_words('<space quantity="1" unit="character"/>')
        self.assertEqual('v.', output)

    def test_g_tag(self):
        for symbol in ['denarius', 'drachma', 'sestercius', 'sestertius', 'leaf']:
            output = highlight_words(f'<g type="{symbol}"/>')
            self.assertEqual(f'(({symbol}))', output)

    def test_example_1(self):
        output = highlight_words("""<supplied reason="lost" >
ἡ
βουλὴ
καὶ
ὁ
δῆμος
</supplied>""")
        self.assertEqual('[ἡ βουλὴ καὶ ὁ δῆμος]', output)
