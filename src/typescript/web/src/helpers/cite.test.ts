import { extractCitationPage, getCite } from "./cite";

describe("helper/cite", () => {
  it("should return valid cite (apa, mla, chicago, bibtex)", () => {
    expect(
      getCite({
        author: "M. Sohail",
        journal: "DESALINATION AND WATER TREATMENT",
        title:
          "Estimation of water quality, management and risk assessment in Khyber-Pakhtunkhwa and Gilgit Baltistan Pakistan",
        year: 2019,
      })
    ).toStrictEqual({
      mla: `M. Sohail et al. "Estimation of water quality, management and risk assessment in Khyber-Pakhtunkhwa and Gilgit Baltistan Pakistan." <em>DESALINATION AND WATER TREATMENT</em> (2019).`,
      apa: `Sohail, M. (2019). Estimation of water quality, management and risk assessment in Khyber-Pakhtunkhwa and Gilgit Baltistan Pakistan. <em>DESALINATION AND WATER TREATMENT</em>.`,
      chicago: `M. Sohail. "Estimation of water quality, management and risk assessment in Khyber-Pakhtunkhwa and Gilgit Baltistan Pakistan." <em>DESALINATION AND WATER TREATMENT</em> (2019).`,
      harvard:
        "Sohail, M., 2019. Estimation of water quality, management and risk assessment in Khyber-Pakhtunkhwa and Gilgit Baltistan Pakistan. <em>DESALINATION AND WATER TREATMENT</em>.",
      bibtex: `@article{Sohail2019Estimation,<br/>title={Estimation of water quality, management and risk assessment in Khyber-Pakhtunkhwa and Gilgit Baltistan Pakistan},<br/>author={M. Sohail},<br/>journal={DESALINATION AND WATER TREATMENT},<br/>year={2019},<br/>doi={}<br/>}`,
    });
  });
  it("should return valid cite (apa, mla, chicago, bibtex) when authors field is set", () => {
    expect(
      getCite({
        authors: [
          "Lefkothea Stella Kremmyda",
          "Eva Tvrzicka",
          "Barbora Stankova",
          "Ales Zak",
        ],
        author: "Lefkothea Stella Kremmyda",
        journal:
          "Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia",
        title:
          "Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.",
        year: 2011,
      })
    ).toStrictEqual({
      mla: 'Lefkothea Stella Kremmyda et al. "Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.." <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em> (2011).',
      apa: "Kremmyda, L., Tvrzicka, E., Stankova, B., & Zak, A. (2011). Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.. <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>.",
      chicago:
        'Lefkothea Stella Kremmyda, Eva Tvrzicka, Barbora Stankova and Ales Zak. "Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.." <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em> (2011).',
      harvard:
        "Kremmyda, L., Tvrzicka, E., Stankova, B., & Zak, A., 2011. Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.. <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>.",
      bibtex:
        "@article{Kremmyda2011Fatty,<br/>title={Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.},<br/>author={Lefkothea Stella Kremmyda and Eva Tvrzicka and Barbora Stankova and Ales Zak},<br/>journal={Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia},<br/>year={2011},<br/>doi={}<br/>}",
    });
  });
  it("should return valid cite (apa, mla, chicago, bibtex) when doi field is set", () => {
    expect(
      getCite({
        authors: [
          "Lefkothea Stella Kremmyda",
          "Eva Tvrzicka",
          "Barbora Stankova",
          "Ales Zak",
        ],
        author: "Lefkothea Stella Kremmyda",
        journal:
          "Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia",
        title:
          "Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.",
        year: 2011,
        doi: "10.2307/3261241",
      })
    ).toStrictEqual({
      mla: "Lefkothea Stella Kremmyda et al. \"Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease..\" <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em> (2011). <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      apa: "Kremmyda, L., Tvrzicka, E., Stankova, B., & Zak, A. (2011). Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.. <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>. <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      chicago:
        "Lefkothea Stella Kremmyda, Eva Tvrzicka, Barbora Stankova and Ales Zak. \"Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease..\" <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em> (2011). <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      harvard:
        "Kremmyda, L., Tvrzicka, E., Stankova, B., & Zak, A., 2011. Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.. <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>. <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      bibtex:
        "@article{Kremmyda2011Fatty,<br/>title={Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.},<br/>author={Lefkothea Stella Kremmyda and Eva Tvrzicka and Barbora Stankova and Ales Zak},<br/>journal={Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia},<br/>year={2011},<br/>doi={10.2307/3261241}<br/>}",
    });
  });
  it("should return valid cite (apa, mla, chicago, bibtex) when the volume and page fields are set.", () => {
    expect(
      getCite({
        authors: [
          "Lefkothea Stella Kremmyda",
          "Eva Tvrzicka",
          "Barbora Stankova",
          "Ales Zak",
        ],
        author: "Lefkothea Stella Kremmyda",
        journal:
          "Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia",
        title:
          "Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.",
        year: 2011,
        doi: "10.2307/3261241",
        pages: "10-12p",
        volume: "1",
      })
    ).toStrictEqual({
      mla: "Lefkothea Stella Kremmyda et al. \"Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease..\" <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>, 1 (2011): 10-12p. <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      apa: "Kremmyda, L., Tvrzicka, E., Stankova, B., & Zak, A. (2011). Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.. <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>, 1, 10-12p. <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      chicago:
        "Lefkothea Stella Kremmyda, Eva Tvrzicka, Barbora Stankova and Ales Zak. \"Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease..\" <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>, 1 (2011): 10-12p. <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      harvard:
        "Kremmyda, L., Tvrzicka, E., Stankova, B., & Zak, A., 2011. Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.. <em>Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia</em>, 1, pp. 10-12p. <a style='color: rgb(8 83 148 / 1);' href='https://doi.org/10.2307/3261241' target='_blank'>https://doi.org/10.2307/3261241</a>.",
      bibtex:
        "@article{Kremmyda2011Fatty,<br/>title={Fatty acids as biocompounds: their role in human metabolism, health and disease: a review. part 2: fatty acid physiological roles and applications in human health and disease.},<br/>author={Lefkothea Stella Kremmyda and Eva Tvrzicka and Barbora Stankova and Ales Zak},<br/>journal={Biomedical papers of the Medical Faculty of the University Palacky, Olomouc, Czechoslovakia},<br/>year={2011},<br/>volume={1},<br/>pages={10-12p},<br/>doi={10.2307/3261241}<br/>}",
    });
  });
  it("should return the values of firstPage and lastPage", () => {
    expect(extractCitationPage("10-12p")).toStrictEqual({
      firstPage: "10",
      lastPage: "12",
    });
  });
  it("should return firstPage and lastPage with empty values.", () => {
    expect(extractCitationPage("")).toStrictEqual({
      firstPage: "",
      lastPage: "",
    });
  });
});
