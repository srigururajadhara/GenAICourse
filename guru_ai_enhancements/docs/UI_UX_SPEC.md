# Guru — UI/UX Specification: Field to Future

**Version:** 0.1  
**Status:** Visual direction accepted in principle; detailed specification pending approval  
**Date:** 15 November 2026

## 1. Design intent

Create a distinctive Guru product experience named **Field to Future**: modern agricultural intelligence with warmth, clarity and trust. It should feel purpose-built for Guru rather than like a generic admin dashboard or a recoloured copy of another product.

The product owner accepted this visual direction in principle. This document defines the proposed design rules to be reviewed before implementation.

## 2. Confirmed usability defect

The user supplied a screenshot with the Irrigation dropdown open. The unselected options (including “Not specified”, “Rainfed”, “Canal”, “Borewell” and “Other”) were dark green text on a near-black menu background. Only the selected option “Drip / sprinkler” had a light background. This made the open menu options difficult to read.

This is a P0 usability defect. It must be tested while the dropdown is open; styling only the closed select control is not sufficient.

## 3. Proposed design tokens

| Token | Proposed value | Usage |
|---|---|---|
| Deep forest | `#173D2D` | Brand surfaces, primary headings on light surfaces |
| Forest shade | `#102E24` | Sidebar or deep brand panels; use white text |
| Leaf green | `#4F8057` | Secondary accents and selected indicators |
| Primary text | `#1C2B24` | Body text on light surfaces |
| Secondary text | `#52635A` | Supporting text on light surfaces |
| Warm ivory | `#F5F3E9` | Main page background |
| Pure white | `#FFFFFF` | Cards, forms, dropdown menus and chat surfaces |
| Soft sage | `#E5EFE5` | Selected/hover surfaces with dark text |
| Harvest gold | `#E4B85D` | Small emphasis/highlight accents; do not use for long text |
| Earth terracotta | `#BD7655` | Secondary accent for status/illustration, not low-contrast body text |

Colour is not the only signal for status; use labels/icons in addition to colour. Keep all colour tokens centralised and documented in the implementation after approval.

Approximate contrast checks for the proposed key text pairs (calculated from the listed sRGB hex values):

| Foreground | Background | Contrast | Intended use |
|---|---|---:|---|
| `#173D2D` | `#FFFFFF` | 12.06:1 | Primary text on white |
| `#102E24` | `#FFFFFF` | 14.60:1 | White text on forest panel (reverse pairing) |
| `#52635A` | `#FFFFFF` | 6.38:1 | Secondary text on white |
| `#173D2D` | `#F5F3E9` | 10.84:1 | Primary text on warm ivory |
| `#52635A` | `#F5F3E9` | 5.74:1 | Secondary text on warm ivory |
| `#173D2D` | `#E5EFE5` | 10.22:1 | Selected text on soft sage |
| `#4F8057` | `#FFFFFF` | 4.61:1 | Accent text; use cautiously for normal-size text |

The final rendered UI must be re-tested; these token-pair calculations do not prove that every real component passes.

## 4. Typography and hierarchy

- Use a consistent readable sans-serif family with locally available fallback fonts.
- Define a clear hierarchy for page title, section title, card title, body, labels and helper text.
- Avoid tiny captions for important instructions, citations or error messages.
- Use a comfortable body-text line height and avoid long full-width text blocks.
- Maintain consistent font weights; reserve extra-bold weights for the product name and major headings.

Proposed minimum design sizes (to validate in the actual UI): body 15–16 px, control labels 14 px, helper/caption text at least 12–13 px, primary section title 20–24 px. Smaller text may be used only for low-priority metadata if it remains readable at normal zoom.

## 5. Dropdown requirements

Applies to State, District (if implemented as a list), Farmer type, Category, Irrigation, Answer language, Document applies to, Document category and all future select controls.

### Closed state

- Light surface with dark selected text.
- Visible border and clear arrow indicator.
- Selected value remains readable at standard browser zoom.

### Open menu state

- Light/white menu surface (`#FFFFFF` or approved equivalent).
- Dark option text (`#1C2B24` or approved equivalent).
- Unselected options remain readable.
- Selected option has a light sage background and dark text, plus a check/selection indicator where supported.
- Hover and keyboard-focus states are visually distinct from selected state.
- No dark text on near-black backgrounds and no colour-only distinction.
- Menu must not be clipped by the sidebar or viewport.

### Interaction and compatibility

- Keyboard users can open, navigate, select and dismiss options.
- Focus indicator is visible.
- Test the actual open menu in Chrome on macOS, which is the current user environment. Add other browsers to the support matrix only after agreement.
- Streamlit/BaseWeb/native menu popovers may be rendered outside the select control DOM or styled differently by browser/OS. The implementation must inspect the rendered open menu. If reliable CSS styling is not possible, evaluate an accessible custom select component; do not ship a visually correct closed control with an unreadable opened menu.

## 6. Buttons and controls

- Primary action: forest green background with white text.
- Secondary action: white or soft-sage surface with dark forest text and visible border.
- Disabled action: readable neutral surface and text; never use very low opacity or dark text on dark background.
- Hover, pressed and focus states must be visible and consistent.
- Suggested prompt buttons (“PM-KISAN details”, “Crop insurance”, “Irrigation subsidy”) must remain readable whether enabled or disabled.
- Inputs and chat composer must have readable placeholder and entered text.

## 7. Screen composition

### Desktop

- Strong brand/hero area with a short, useful product message.
- Clear knowledge-base health metrics.
- Main working area focused on the chat, not excessive empty space.
- Farmer profile presented as a supporting panel that does not compete with the chat.
- Document upload and knowledge-base management clearly separated from question answering.

### Tablet and mobile

- Sidebar information moves into a usable compact navigation or profile panel.
- Chat composer and action buttons remain visible and tappable.
- Cards stack without horizontal clipping.
- Dropdown menu and evidence panels stay within the viewport.

## 8. Chat experience

- User and Guru messages must be visually distinguishable without colour alone.
- Loading state explains that Guru is retrieving documents and composing an answer.
- Evidence appears in a clearly identified source panel with document name, page number and excerpt.
- Abstention/insufficient-evidence messages must not look like application errors.
- API/ingestion failures must look distinct from a model's abstention response.
- Do not hide citations in tiny caption text.

## 9. Accessibility target

Proposed target: WCAG 2.2 AA for applicable text and UI contrast. Check normal text at 4.5:1, large text at 3:1, and relevant non-text control/focus boundaries at 3:1. Provide keyboard access and visible focus. The target must be checked using the final rendered colours and not only token names.

## 10. Originality and asset rules

- Create a Guru-specific layout, visual language, icon grouping, empty states, labels and component details.
- Do not copy another product's exact page composition, illustrations, logo, text or styling.
- Use original or appropriately licensed fonts/icons/illustrations and record their sources in an asset register.
- “Unique” means an original Guru design created for this project; it is not a legal or factual claim that no similar design exists anywhere.

## 11. UX acceptance checklist

- [ ] Every dropdown opened in the supported browser has readable option text.
- [ ] Selected, unselected, hover, focus and disabled states are distinguishable.
- [ ] All text/background combinations meet the agreed contrast target.
- [ ] Suggested buttons remain readable when disabled.
- [ ] Inputs, placeholders, tabs, alerts, evidence panels and footer are readable.
- [ ] Keyboard-only navigation works for all primary controls.
- [ ] Desktop, tablet and mobile layouts have no clipped content.
- [ ] The design is recognisably Guru and not a copied template.
- [ ] Existing baseline capabilities remain available.


## 12. Standards references

- [W3C WCAG 2.2 — Contrast (Minimum), Success Criterion 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): normal text 4.5:1; large text 3:1.
- [W3C WCAG 2.2 — Non-text Contrast, Success Criterion 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast): meaningful UI component/state indicators and graphical objects 3:1 against adjacent colours.
