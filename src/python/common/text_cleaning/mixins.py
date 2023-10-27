import re


class TextCleaningMixins(object):
    @property
    def re_currency(self):
        CURRENCY_REGEX = re.compile(
            "({})+".format("|".join(re.escape(c) for c in self.currencies_dict.keys()))
        )
        return CURRENCY_REGEX

    @property
    def re_email(self):
        EMAIL_REGEX = re.compile(
            r"(?:^|(?<=[^\w@.)]))([\w+-](\.(?!\.))?)*?[\w+-](@|[(<{\[]at[)>}\]])(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))",  # noqa: E501
            flags=re.IGNORECASE | re.UNICODE,
        )
        return EMAIL_REGEX

    @property
    def single_quote_list(self):
        single_quotes = ["‘", "‛", "’", "❛", "❜", "`", "´", "‘", "’"]
        return single_quotes

    @property
    def double_quote_list(self):
        double_quotes = [
            "«",
            "‹",
            "»",
            "›",
            "„",
            "“",
            "‟",
            "”",
            "❝",
            "❞",
            "❮",
            "❯",
            "〝",
            "〞",
            "〟",
            "＂",
        ]

        return double_quotes

    @property
    def re_single_quote(self):
        single_quotes_dict = {k: "'" for k in self.single_quote_list}
        return single_quotes_dict

    @property
    def single_quote_compile(self):
        SINGLE_QUOTE_REGEX = re.compile("|".join(self.single_quote_list))
        return SINGLE_QUOTE_REGEX

    @property
    def re_double_quote(self):
        double_quotes_dict = {k: '"' for k in self.double_quote_list}
        return double_quotes_dict

    @property
    def double_quote_compile(self):
        DOUBLE_QUOTE_REGEX = re.compile("|".join(self.double_quote_list))
        return DOUBLE_QUOTE_REGEX

    @property
    def re_url(self):
        URL_REGEX = re.compile(
            r"(?:^|(?<![\w\/\.]))"
            # protocol identifier
            # r"(?:(?:https?|ftp)://)"  <-- alt?
            r"(?:(?:https?:\/\/|ftp:\/\/|www\d{0,3}\.))"
            # user:pass authentication
            r"(?:\S+(?::\S*)?@)?" r"(?:"
            # IP address exclusion
            # private & local networks
            r"(?!(?:10|127)(?:\.\d{1,3}){3})"
            r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
            r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
            # IP address dotted notation octets
            # excludes loopback network 0.0.0.0
            # excludes reserved space >= 224.0.0.0
            # excludes network & broadcast addresses
            # (first & last IP address of each class)
            r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
            r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
            r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
            r"|"
            # host name
            r"(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)"
            # domain name
            r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
            # TLD identifier
            r"(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))" r"|" r"(?:(localhost))" r")"
            # port number
            r"(?::\d{2,5})?"
            # resource path
            r"(?:\/[^\)\]\}\s]*)?",
            flags=re.UNICODE | re.IGNORECASE,
        )
        return URL_REGEX

    @property
    def abbreviations_dict(self) -> dict[str, str]:
        abbreviations_dict = {
            "A.D.": "AD",
            "A.I.": "AI",
            "a.m.": "am",
            "ca.": "ca",
            "Cap.": "Cap",
            "cf.": "cf",
            "C.P.": "CP",
            "C.V.": "CV",
            "cwt.": "cwt",
            "D.V.": "DV",
            "D.G.": "DG",
            "ead.": "ead",
            "et al.": "et al",
            "et.al": "et al",
            "etc.": "etc",
            "e.g.": "eg",
            "fac.": "fac",
            "fl.": "fl",
            "ibid.": "ibid",
            "id.": "id",
            "i.a.": "ia",
            "i.e.": "ie",
            "J.D.": "JD",
            "lb.": "lb",
            "lbs.": "lbs",
            "LL.B.": "LLB",
            "M.A.": "MA",
            "M.O.": "MO",
            "N.B.": "NB",
            "nem. con.": "nem con",
            "op. cit.": "op cit",
            "O.V.": "OV",
            "P.A.": "PA",
            "per cent.": "per cent",
            "Ph.D.": "PhD",
            "p.m.": "pm",
            "P.M.A.": "PMA",
            "P.P.per pro.": "PPper pro",
            "P.R.N.": "PRN",
            "pro tem.": "pro tem",
            "P.S.": "PS",
            "P.P.S.": "PPS",
            "Q.D.": "QD",
            "Q.E.D.": "QED",
            "q.v.qq.v.": "qvqqv",
            "Reg.": "Reg",
            "r.": "r",
            "R.I.P.": "RIP",
            "S.A.": "SA",
            "sc.scil.": "scscil",
            "S.L.": "SL",
            "S.S.": "SS",
            "S.O.S.": "SOS",
            "stat.": "stat",
            "viz.": "viz",
            "vs.": "vs",
            "v.": "v.",
            "A.B.": "AB",
            "a.C.n.": "aCn",
            "ad. nat. delt.": "ad nat delt",
            "A.M.D.G.": "AMDG",
            "An. Sal.": "An Sal",
            "a.u.": "au",
            "a.U.c.": "aUc",
            "B.A.": "BA",
            "CC.": "CC",
            "D.D.": "DD",
            "D.Lit.D.Litt.": "DLitDLitt",
            "D.M.": "DM",
            "D.M.D.": "DMD",
            "D.Phil.": "DPhil",
            "D.Sc.": "DSc",
            "D. S. P.": "DSP",
            "D.Th.": "DTh",
            "Ed.D.": "EdD",
            "et ux.": "et ux",
            "dwt.": "dwt",
            "F.D.FID.DEF.": "FDFIDDEF",
            "I.N.D.F.S.S.A.": "INDFSSA",
            "in litt.": "in litt",
            "inst.": "inst",
            "J.S.D.": "JSD",
            "Lit.D.Litt.D.": "LitDLittD",
            "Ll.D.": "LlD",
            "Ll.M.": "LlM",
            "loq.": "loq",
            "M.D.": "MD",
            "m.m.": "mm",
            "N.I.A.": "NIA",
            "N.N.": "NN",
            "Nob.": "Nob",
            "O.D.": "OD",
            "O.H.S.S.": "OHSS",
            "O.S.": "OS",
            "O.U.": "OU",
            "per mil.": "per mil",
            "prox.": "prox",
            "Q.D.B.V.": "QDBV",
            "Q.E.C.": "QEC",
            "Q.E.F.": "QEF",
            "Q.E.I.": "QEI",
            "sc.": "sc",
            "sec.": "sec",
            "S.C.S": "SCS",
            "S.C.S.D.X": "SCSDX",
            "S.D.X": "SDX",
            "S.D.I.X": "SDIX",
            "S.J.D.": "SJD",
            "Sc.D.": "ScD",
            "sphalm.": "sphalm",
            "S.P.D.": "SPD",
            "S.P.Q.R.": "SPQR",
            "sqq.": "sqq",
            "S.S. Theol.": "SS Theol",
            "S.T.T.L.": "STTL",
            "s.v.": "sv",
            "S.V.B.E.E.V.": "SVBEEV",
            "Th.D.": "ThD",
            "ult.": "ult",
            "u.s.": "us",
            "V.C.": "VC",
            "V.I.": "VI",
            "v.i.": "vi",
            "v.s.": "vs",
        }

        return abbreviations_dict

    @property
    def titles_dict(self) -> dict[str, str]:
        titles_dict = {"Mr.": "Mr ", "Ms.": "Ms ", "Mrs.": "Mrs ", "Dr.": "Dr "}

        return titles_dict

    @property
    def currencies_dict(self) -> dict[str, str]:
        currencies_dict = {
            "$": "USD",
            "zł": "PLN",
            "£": "GBP",
            "¥": "JPY",
            "฿": "THB",
            "₡": "CRC",
            "₦": "NGN",
            "₩": "KRW",
            "₪": "ILS",
            "₫": "VND",
            "€": "EUR",
            "₱": "PHP",
            "₲": "PYG",
            "₴": "UAH",
            "₹": "INR",
            "﷼": "IRR",
        }

        return currencies_dict

    @property
    def re_patters(self):
        re_patterns = {
            "_": "",
            # f"([{punctuation}])\\1+": "\\1",
            r"\[\s*(.*?)\s*\]": r"[\1]",
            r"\(\s*(.*?)\s*\)": r"(\1)",
            r"""((?<=[A-Za-z0-9])\.(?=[A-Za-z]{2})|(?<=[A-Za-z]{2})\.(?=[A-Za-z0-9]))""": ". ",
            r"(?<=[,:;!?])(?=[^\s])": r" ",
            r'\s([?.!"](?:\s|$))': r"\1",
            r"<.*?>": "",
        }

        return re_patterns

    @property
    def re_replace_dict(self):
        re_replace_dict = {
            **self.currencies_dict,
            **self.titles_dict,
            **self.abbreviations_dict,
            **self.re_single_quote,
            **self.re_double_quote,
            **self.re_patters,
        }
        return re_replace_dict
