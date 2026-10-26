# Long-term convention intake, 2026-10-26

Research intake, not implemented coverage or a physical accuracy certificate.
No competing implementation source was consulted. Mathematical definitions
were read from the public theory manual and the primary works below.

Existing seven distinct conventions are retained. Proposed additions:

| Key | Definition |
|---|---|
| lahiri_icrc | JD 2435553.5 TT, 23 degrees 15 minutes true; remove reference nutation |
| lahiri_1940 | JD 2415020.0 TT, 22 degrees 26 minutes 45.50 seconds |
| kp_senthilathiban | JD 1827424.7572800927 TT, zero |
| sassanian | JD 1927135.8747793 ET represented as TT, zero |
| true_revati | zeta Psc A ordinary longitude fixed at 359 degrees 50 minutes |
| true_mula | lambda Sco ordinary longitude fixed at 240 degrees |
| aldebaran | alpha Tau ordinary longitude fixed at 45 degrees |
| galactic_center_sagittarius | Sgr A* ordinary longitude fixed at 240 degrees |
| galactic_center_capricorn | Sgr A* ordinary longitude fixed at 270 degrees |
| dhruva_middle_mula | Sgr A* polar longitude fixed at 246 degrees 40 minutes |
| galactic_equator_iau1958 | ascending intersection of transformed IAU-1958 plane and mean ecliptic fixed at 240 degrees |
| galactic_equator_modern | ascending intersection of Liu/Zhu/Zhang proposed ICRS plane and mean ecliptic fixed at 240 degrees |
| ardra_galactic_plane | same proposed plane intersection fixed at 246 degrees 40 minutes |
| suryasiddhanta_equinox | Julian 499-03-21 07:30:31.57 UT1, zero |
| suryasiddhanta_mean_sun | same instant, -0.21463395 degrees |
| aryabhata_equinox | Julian 499-03-21 06:56:55.57 UT1, zero |
| aryabhata_mean_sun | same instant, -0.23763238 degrees |
| aryabhata_522 | Julian 522-03-21 05:46:44 UT1, zero |
| suryasiddhanta_revati | same 499 SS instant, -0.79167046 degrees |
| suryasiddhanta_citra | same 499 SS instant, +2.11070444 degrees |

The last seven are **historical operations with a modern realization**. The
ancient texts do not specify TT, Delta-T, these exact modern UT1 instants, or
the modern mean-Sun reductions. The 522 text supports a year tradition, not
the exact day and time. A software policy must retain that distinction and
freeze the Julian calendar, astronomical year numbering, Ujjain/Lanka meridian
realization, Espenak/Meeus Delta-T conversion and Vondrak transport. They must
never be presented as exact author-canonical constants.

IAU-1958 transformed J2000/ICRS pole: RA 192.85948125 degrees,
declination 27.1282511111 degrees. Proposed Liu/Zhu/Zhang pole: RA
192.902979992083 degrees, declination 27.103109214444 degrees. The latter is
a proposed coordinate convention, not an IAU-adopted physical truth. With
galactic pole p and date ecliptic pole q, p cross q selects the ascending node.
Polar longitude projects an object's celestial meridian onto the ecliptic;
it is not the object's ordinary ecliptic longitude.

Stellar component choice, catalog uncertainty and propagation interval need
their own receipts. The current stellar catalog contains only Spica and delta
Cancri. Numerical evaluation of a convention with a supplied date-specific
anchor does not qualify the missing astrophysical calculation.

Sources:

- [Public theory manual, sections 2.8.3-2.8.9](https://www.astro.com/swisseph/swisseph.htm)
- [Aryabhatiya primary translation](https://en.wikisource.org/wiki/The_Aryabhatiya_of_Aryabhata)
- [Ramasubramanian, Astronomy of Aryabhata](https://www.asindia.org/assets/files/astronomy_of_aryabhata.pdf)
- [Calendar Reform Committee report](https://dspace.gipe.ac.in/xmlui/bitstream/handle/10973/39692/GIPE-043972.pdf?isAllowed=y&sequence=3)
- [Surya-Siddhanta translation](https://commons.wikimedia.org/wiki/File:TRANSLATION_OF_THE_SURYA-SIDDHANTA_(IA_dli.bengal.10689.17955).pdf)
- [Liu/Zhu/Hu 2011](https://www.aanda.org/articles/aa/pdf/2011/12/aa16947-11.pdf)
- [Liu/Zhu/Zhang 2011](https://doi.org/10.1051/0004-6361/201014961)
- [Vondrak 2011 presentation](https://syrte.obspm.fr/jsr/journees2011/pdf/vondrak.pdf)
- [sofars 0.6.1 license including SOFA terms](https://raw.githubusercontent.com/astro-xao/sofars/v0.6.1/LICENSE)

The sofars dependency has not yet been added. Its complete license was read;
MIT permission and SOFA derived-work notices must be retained if it is used.
No source from that dependency has yet been copied or modified.
