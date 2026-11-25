// Extract past-paper questions into JSON, one file per paper:
//
//   Edexcel A (9EC0 / 8EC0): every section of Papers 1 and 2 - Section A's
//     written parts only, its MCQs being Phase 7's - and both sections of
//     Paper 3, into edexcel-a/ and edexcel-a-as/. See extractSectionA().
//   Edexcel B (9EB0 / 8EB0): every question of every paper - B has no
//     multiple choice and no optional questions - into edexcel-b/ and
//     edexcel-b-as/. See extractB().
//
//   swift scripts/extract_past_paper_questions.swift <question-paper.pdf> ...
//
// Run from the repo root. Writes past-paper-questions-data/<dir>/<paper>-<series>.json
// and prints a one-line summary per paper to stderr. The board is read from the
// filename: edexcel-b-* files are routed to the B parser before the Edexcel A
// pattern is tried, because that pattern matches a B filename too.
//
// Why Swift: this repo has no Python PDF library, no requirements.txt and no
// venv, but macOS ships PDFKit. docs/QUESTIONS_PROGRESS.md section 7 already
// established Swift + PDFKit as the working method for these PDFs. Zero new
// dependencies.
//
// This script NEVER invents, paraphrases or reconstructs question text. If a
// question cannot be located or its mark scheme page cannot be verified, the
// question is emitted with confidence "low" and a note, or omitted entirely and
// recorded in "problems". Both are then chased by hand in the QA report.
//
// Topic and keyword tagging is deliberately NOT done here. It lives in
// past-paper-questions-data/tags.json, hand-written, so that re-running this
// extractor can never destroy it.

import Foundation
import PDFKit

// ------------------------------------------------------------------ helpers

func rx(_ pattern: String, _ opts: NSRegularExpression.Options = []) -> NSRegularExpression {
    // swiftlint:disable:next force_try
    return try! NSRegularExpression(pattern: pattern, options: opts)
}

extension NSRegularExpression {
    func firstMatch(_ s: String) -> [String?]? {
        let ns = s as NSString
        guard let m = firstMatch(in: s, range: NSRange(location: 0, length: ns.length)) else {
            return nil
        }
        return (0..<m.numberOfRanges).map { i in
            m.range(at: i).location == NSNotFound ? nil : ns.substring(with: m.range(at: i))
        }
    }

    func allMatches(_ s: String) -> [[String?]] {
        let ns = s as NSString
        return matches(in: s, range: NSRange(location: 0, length: ns.length)).map { m in
            (0..<m.numberOfRanges).map { i in
                m.range(at: i).location == NSNotFound ? nil : ns.substring(with: m.range(at: i))
            }
        }
    }

    func matches(_ s: String) -> Bool {
        let ns = s as NSString
        return firstMatch(in: s, range: NSRange(location: 0, length: ns.length)) != nil
    }
}

/// Page furniture that appears on every page and is never part of a question.
///
/// The margin warnings are rotated 90 degrees in the artwork, so PDFKit drops
/// them into the reading order at arbitrary points — mid-sentence, or ahead of
/// the question number. They therefore cannot be anchored to a line.
let furniture: [NSRegularExpression] = [
    rx("\\*[A-Z]\\d{5,6}[A-Z]?\\d{4,6}\\*"),   // *P57190A01032*
    rx("DO NOT WRITE IN THIS AREA"),
    rx("BLANK PAGE"),
    rx("(?m)^\\s*Turn over\\s*$"),
    rx("(?m)^\\s*\\d{1,3}\\s*$"),               // bare page number on its own line
]

/// A space inside a URL is always a line-wrap artefact — URLs cannot contain
/// one — so joining them back up repairs the link rather than altering wording.
/// Only whitespace directly after a URL-punctuation character is removed, and
/// only inside a run that started with http:// or https://.
/// A run of non-space characters, admitting a space only where the character
/// before it is URL punctuation and a non-space follows. Written as an
/// alternation inside the repeat so the engine cannot settle on a greedy
/// prefix and skip the wrapped remainder.
let urlSpan = rx("https?://(?:\\S|(?<=[-/._?=&])\\s(?=\\S))+")
let urlWrap = rx("(?<=[-/._?=&])\\s+")

func repairURLs(_ s: String) -> String {
    let ns = s as NSString
    var result = ""
    var cursor = 0
    for m in urlSpan.matches(in: s, range: NSRange(location: 0, length: ns.length)) {
        result += ns.substring(with: NSRange(location: cursor, length: m.range.location - cursor))
        let span = ns.substring(with: m.range)
        result += urlWrap.stringByReplacingMatches(
            in: span, range: NSRange(location: 0, length: (span as NSString).length),
            withTemplate: "")
        cursor = m.range.location + m.range.length
    }
    result += ns.substring(from: cursor)
    return result
}

/// Runs of the dotted answer-line leaders, plus any line made only of dots.
let dotLeader = rx("\\.{6,}[\\s\\.]*")

/// Pearson's provenance note, printed under the stimulus paragraph of a
/// Section C question: `(Source adapted from: https://...)`, and three other
/// orderings of the same words. It is where the stimulus came from, not part of
/// what the candidate is asked to do, so it is lifted out into its own field
/// rather than left in the middle of the question.
///
/// The URL is required, which is what keeps ordinary prose safe - these
/// questions use the word freely ("a source of market failure"), and none of
/// those sit in brackets around a link. `[^()]` rather than `.` so a citation
/// can never swallow a later bracket - but one balanced pair is allowed inside
/// it, because a URL can carry one: Paper 2 June 2025 Q8 cites
/// ".../PIIS0140-6736(23)00858-9/fulltext". Kept identical to ATTRIBUTION in
/// strip_source_attributions.py, so the safety net sees what this sees.
///
/// Run after repairURLs, so a citation whose URL wrapped across a line is one
/// span by the time this sees it. Mirrors `clean()` in extract_aqa_questions.py,
/// which drops AQA's equivalent `Sources:` line.
let attribution = rx(
    "\\(\\s*Sources?\\b(?:[^()]|\\([^()]*\\))*https?://(?:[^()]|\\([^()]*\\))*\\)")

/// Returns the text without its citation, and the citation itself.
func stripAttribution(_ s: String) -> (text: String, attribution: String?) {
    let ns = s as NSString
    let all = attribution.matches(in: s, range: NSRange(location: 0, length: ns.length))
    guard !all.isEmpty else { return (s, nil) }

    let found = all.map { ns.substring(with: $0.range) }.joined(separator: " ")
    var out = attribution.stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: ns.length), withTemplate: " ")
    // The citation sits between the stimulus and the question sentence, so
    // taking it out leaves two spaces mid-string and one at the end.
    out = rx("\\s{2,}").stringByReplacingMatches(
        in: out, range: NSRange(location: 0, length: (out as NSString).length),
        withTemplate: " ")
    out = rx("\\s+([.,;:!?])").stringByReplacingMatches(
        in: out, range: NSRange(location: 0, length: (out as NSString).length),
        withTemplate: "$1")
    return (out.trimmingCharacters(in: .whitespacesAndNewlines), found)
}

func stripFurniture(_ raw: String) -> String {
    var s = raw
    for r in furniture {
        s = r.stringByReplacingMatches(
            in: s, range: NSRange(location: 0, length: (s as NSString).length),
            withTemplate: " ")
    }
    s = dotLeader.stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: (s as NSString).length), withTemplate: " ")
    return s
}

/// Collapse a question's text to a single clean paragraph-preserving string.
/// Line breaks inside a PDF are typographic, not semantic, so they are joined.
func normalise(_ raw: String) -> String {
    var s = stripFurniture(raw)
    s = s.replacingOccurrences(of: "\u{00A0}", with: " ")
    s = s.components(separatedBy: .newlines)
        .map { $0.trimmingCharacters(in: .whitespaces) }
        .filter { !$0.isEmpty }
        .joined(separator: " ")
    s = rx("\\s{2,}").stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: (s as NSString).length), withTemplate: " ")
    s = repairURLs(s)
    // A lone full stop left behind by the answer-line leaders. The leader run is
    // stripped by dotLeader, but where the PDF spaces the first dot away from
    // the rest ("workers. . . . . . . . .") that first one survives on its own.
    // Only ever removed at the very end of the text, so an ellipsis or a
    // decimal point mid-sentence cannot be touched.
    s = rx("\\s+\\.\\s*$").stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: (s as NSString).length), withTemplate: "")
    return s.trimmingCharacters(in: .whitespacesAndNewlines)
}

// ------------------------------------------------------------------ model

struct QuestionOut {
    var id: String
    var section: String
    var questionNumber: String
    var parentQuestion: String?
    var choiceGroup: String?
    var marks: Int
    var questionText: String
    /// Pearson's citation for the stimulus, lifted out of questionText. Kept so
    /// the provenance is not destroyed, but never emitted into questions.json,
    /// so it stays out of the card and out of the search index.
    var sourceAttribution: String?
    var contextPage: Int?
    /// "extracts" (Section B's extract block, and every record before Phase 6)
    /// or "question" (Section A: the page the question's stem is printed on).
    var contextType: String = "extracts"
    var qpPage: Int
    var msPage: Int?
    var msVerified: Bool
    var confidence: String
    var notes: [String]
}

struct PaperMeta {
    var paper: Int
    var paperName: String
    var year: Int
    var series: String
    var seriesSlug: String
    var qpPath: String
    var msPath: String
    var idStem: String
    var qualification: String
    /// "a-level" or "as-level". Drives the output directory as well as the
    /// record, because both qualifications have a Paper 1 in the same series and
    /// the filenames would otherwise collide.
    var level: String
    var isAS: Bool { level == "as-level" }
    // Board identity and output directory travel with the paper, so an
    // Edexcel B file can never be written into edexcel-a/. The defaults are
    // Edexcel A's, which keeps its output byte-identical.
    var board: String = "edexcel"
    var boardName: String = "Edexcel"
    var outDir: String = ""
    var isB: Bool { board == "edexcel-b" }
}

/// 9EB0 / 8EB0 paper names, as printed on the covers (all 36 covers with a
/// text layer agree, bar spacing).
let bPaperNames = [
    1: "Markets and how they work",
    2: "Competing in the global economy",
    3: "The economic environment and business",
]
let bASPaperNames = [
    1: "Markets, consumers and firms",
    2: "The wider economic environment",
]

func parseMetaB(_ path: String) -> PaperMeta? {
    let file = (path as NSString).lastPathComponent
    guard
        let m = rx("^edexcel-b-(a|as)-level-economics-paper-(\\d)-([a-z]+)-(\\d{4})-question-paper\\.pdf$")
            .firstMatch(file),
        let paper = Int(m[2]!), let year = Int(m[4]!),
        let seriesName = seriesNames[m[3]!]
    else { return nil }
    let isAS = m[1]! == "as"
    guard let paperName = (isAS ? bASPaperNames : bPaperNames)[paper] else { return nil }
    let short = String(seriesName.lowercased().prefix(3))
    let stem = isAS ? "edexcel-b-as" : "edexcel-b"
    var meta = PaperMeta(
        paper: paper, paperName: paperName, year: year, series: seriesName,
        seriesSlug: "\(m[3]!)-\(year)", qpPath: path,
        msPath: path.replacingOccurrences(of: "-question-paper.pdf", with: "-mark-scheme.pdf"),
        idStem: "\(stem)-p\(paper)-\(year)-\(short)",
        qualification: isAS ? "AS Level Economics B (8EB0)" : "A Level Economics B (9EB0)",
        level: isAS ? "as-level" : "a-level")
    meta.board = "edexcel-b"
    meta.boardName = "Edexcel B"
    meta.outDir = isAS ? "edexcel-b-as" : "edexcel-b"
    return meta
}

// The 2024 covers abbreviate two of these ("Market and Business Behaviour",
// "Micro and Macro Economics"); the specification names are used instead.
let paperNames = [
    1: "Markets and Business Behaviour",
    2: "The National and Global Economy",
    3: "Microeconomics and Macroeconomics",
]

/// 8EC0 is a different qualification with different papers, not a subset of
/// 9EC0: two papers, both named differently from their A Level counterparts.
/// Taken from the covers. The 2016 covers set them in sentence case; the
/// specification's title case is used, matching how paperNames treats 9EC0.
let asPaperNames = [
    1: "Introduction to Markets and Market Failure",
    2: "The UK Economy – Performance and Policies",
]

let seriesNames = ["june": "June", "october": "October", "november": "November"]

func parseMeta(_ path: String) -> PaperMeta? {
    let file = (path as NSString).lastPathComponent
    let isAS = path.contains("/as-level/")
    guard
        let m = rx("paper-(\\d)-([a-z]+)-(\\d{4})-question-paper\\.pdf$").firstMatch(file),
        let paper = Int(m[1]!), let year = Int(m[3]!),
        let seriesName = seriesNames[m[2]!],
        let paperName = (isAS ? asPaperNames : paperNames)[paper]
    else { return nil }

    let seriesSlug = "\(m[2]!)-\(year)"
    let msPath = path.replacingOccurrences(
        of: "-question-paper.pdf", with: "-mark-scheme.pdf")
    let short = String(seriesName.lowercased().prefix(3))
    // "edexcel-as-" rather than "edexcel-a-as-": the ids are the visible anchor
    // on every card, and the two stems have to be told apart at a glance.
    let stem = isAS ? "edexcel-as" : "edexcel-a"
    return PaperMeta(
        paper: paper, paperName: paperName, year: year, series: seriesName,
        seriesSlug: seriesSlug, qpPath: path, msPath: msPath,
        idStem: "\(stem)-p\(paper)-\(year)-\(short)",
        qualification: isAS
            ? "AS Level Economics A (8EC0)" : "A Level Economics A (9EC0)",
        level: isAS ? "as-level" : "a-level")
}

// ------------------------------------------------------------------ mark scheme

/// Mark allocations that always follow a question label in an Edexcel scheme.
/// Used as the signature that a bare label really is a scheme heading.
let allocation = "(?:Knowledge|Analysis|Application|Evaluation|Indicative|The only correct)"

/// Find the first mark-scheme page whose heading names this question.
///
/// Three layouts occur across the sixteen schemes and all three are handled:
///
///  1. PDFKit returns the table header in reading order, interleaving the column
///     labels: "Question Indicative content Mark Number 6(c)". The anchor is
///     "Number" followed by the label, not the contiguous phrase "Question Number".
///  2. Where a question's row spills onto a new page the header stays behind, so
///     the page opens on the bare label: "6(a) Knowledge 1, Application 1".
///     (Paper 1 June 2024.)
///  3. Some schemes space the label: "6 (a)" not "6(a)". (Paper 2 October 2020.)
///
/// Page 1 and 2 are skipped because the cover carries a publications code that
/// can otherwise collide ("Question Paper Log Number 73999").
/// Page number, and whether the question label was matched exactly or by the
/// looser fallback described below.
func markSchemePage(_ pages: [String], question: String, part: String?, bScheme: Bool = false)
    -> (page: Int, exact: Bool)?
{
    // Tolerate "6(a)" and "6 (a)"; reject a longer number ("7" must not hit "70").
    let label: String
    if let part = part {
        label = "\(question)\\s*\\(\\s*\(part)\\s*\\)"
    } else {
        label = "\(question)(?![0-9])"
    }

    // The class holds a literal non-breaking space: ICU's \s does not match one.
    let byHeader = rx("Number[\\s\u{00A0}]*\(label)")
    // \s rather than [ \t] between the label and its allocation: where a
    // question's row spills onto a new page the allocation often wraps onto the
    // line below the label (Paper 3 June 2024, question 1(b)).
    let byBareLabel = rx("(?m)^[ \\t]*\(label)\\s+\(allocation)")

    for (i, page) in pages.enumerated() where i >= 2 {
        if byHeader.matches(page) || byBareLabel.matches(page) {
            return (i + 1, true)
        }
    }

    // 9EB0/8EB0 only (so 9EC0/8EC0 output cannot move): two more
    // layouts. "Question Number Answer 1(a) Knowledge/understanding 1" (Paper 2
    // October 2020, AS Paper 2 June 2016), and the 2024 schemes that reprint
    // the question, wrapping its last words onto the label's line:
    // "1(b) show your working. / Knowledge/understanding 1".
    if bScheme {
        let byAnswer = rx("Number[\\s\u{00A0}]+Answer[\\s\u{00A0}]*\(label)\\s+\(allocation)")
        let byReprint = rx("(?m)^[ \\t]*\(label)[ \\t]+[^\\n]{0,120}\\n[ \\t]*\(allocation)")
        for (i, page) in pages.enumerated() where i >= 2 {
            if byAnswer.matches(page) || byReprint.matches(page) { return (i + 1, true) }
        }
    }

    // Fallback for a scheme that drops the question number from a part heading.
    // Paper 3 November 2021 labels question 2(d) as just "(d)". The "Number"
    // anchor plus a bare part label is still a scheme heading and nothing else,
    // but the match is weaker, so it is reported rather than passed off as exact.
    if let part = part {
        let bare = rx("Number[\\s\u{00A0}]*\\(\\s*\(part)\\s*\\)")
        for (i, page) in pages.enumerated() where i >= 2 {
            if bare.matches(page) { return (i + 1, false) }
        }
    }
    return nil
}

// ------------------------------------------------------------------ section C

/// Section C is one 25-mark essay chosen from two, always Q7 and Q8.
/// Layout: "EITHER  7 <text> (Total for Question 7 = 25 marks)  OR  8 <text> ..."
func extractSectionC(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    var problems: [String] = []

    guard
        let idx = pages.firstIndex(where: {
            $0.contains("SECTION C") && ($0.contains("EITHER") || $0.contains("Answer ONE"))
        })
    else {
        return ([], ["Section C page not found"])
    }

    let page = pages[idx]
    var out: [QuestionOut] = []
    let group = "\(meta.idStem)-sec-c"

    for (n, opener) in [(7, "EITHER"), (8, "OR")] {
        let total = "(Total for Question \(n) = 25 marks)"
        guard let totalRange = page.range(of: total) else {
            problems.append("Q\(n): '(Total for Question \(n) = 25 marks)' not found")
            continue
        }
        // Start after the opener keyword that precedes this question's total.
        let before = String(page[page.startIndex..<totalRange.lowerBound])
        guard let openerRange = before.range(of: opener, options: .backwards) else {
            problems.append("Q\(n): opener '\(opener)' not found before its total line")
            continue
        }
        var body = String(before[openerRange.upperBound...])
        body = normalise(body)
        // Strip the leading question number.
        body = rx("^\(n)\\s+").stringByReplacingMatches(
            in: body, range: NSRange(location: 0, length: (body as NSString).length),
            withTemplate: "")
        // Section C is where Pearson prints the citation, between the stimulus
        // and the instruction. Lift it out before the length checks below, so
        // confidence reflects the question rather than the URL padding it.
        let cited = stripAttribution(body)
        body = cited.text

        var notes: [String] = []
        var confidence = "high"
        if body.count < 60 {
            confidence = "low"
            notes.append("extracted text is suspiciously short (\(body.count) chars)")
        }
        if body.contains("....") {
            confidence = "low"
            notes.append("answer-line leaders survived cleaning")
        }

        let hit = markSchemePage(msPages, question: String(n), part: nil)
        let ms = hit?.page
        if hit == nil {
            confidence = "low"
            notes.append("mark scheme page for Q\(n) could not be verified")
        }

        out.append(
            QuestionOut(
                id: "\(meta.idStem)-q\(n)", section: "C", questionNumber: String(n),
                parentQuestion: nil, choiceGroup: group, marks: 25, questionText: body,
                sourceAttribution: cited.attribution,
                contextPage: nil, qpPage: idx + 1, msPage: ms, msVerified: ms != nil,
                confidence: confidence, notes: notes))
    }

    if out.count != 2 {
        problems.append("expected 2 Section C questions, got \(out.count)")
    }
    return (out, problems)
}

// ------------------------------------------------------------- source booklet

/// June 2025 moved every 9EC0 extract out of its section and into a Source
/// Booklet bound at the back of the paper, one block per section, each headed
/// "Sources for use with SECTION X". Returns the first page index of each
/// block, keyed by section letter. Empty for every earlier paper, whose
/// extracts sit inside their section, and every branch below that depends on
/// it is skipped when it is empty - which is what keeps the output for those
/// papers byte-identical.
func sourceBooklet(_ pages: [String]) -> [(section: String, page: Int)] {
    let heading = rx("Sources for use with SECTION ([A-C])")
    var out: [(section: String, page: Int)] = []
    for (i, page) in pages.enumerated() {
        guard let m = heading.firstMatch(page), let s = m[1] else { continue }
        if !out.contains(where: { $0.section == s }) { out.append((s, i)) }
    }
    return out
}

/// The pages a section's sources occupy in the booklet: from its heading to the
/// next block's heading, or to the end of the paper.
func bookletRange(_ booklet: [(section: String, page: Int)], section: String, pageCount: Int)
    -> Range<Int>?
{
    guard let i = booklet.firstIndex(where: { $0.section == section }) else { return nil }
    let end = i + 1 < booklet.count ? booklet[i + 1].page : pageCount
    return booklet[i].page..<end
}

/// "before answering Question 6", allowing for the 2025 papers, which wrap the
/// instruction mid-phrase ("... in the Source Booklet before\nanswering Question 6").
let beforeAnswering = rx("before\\s+answering\\s+Question\\s+(\\d+)")

/// A booklet paper's section preamble: the heading, the instruction to read the
/// sources, and the timing advice. The 2025 papers set the first part's number
/// ahead of the heading ("6 (a) SECTION B Read Figures 1 and 2 ..."), so left in
/// place it would be read as the opening of part (a). It is instructions to the
/// candidate, not question text, so it is removed, never rewritten.
let bookletPreamble = rx(
    "SECTION [A-C]\\s+Read\\b.*?You are advised to spend[^\\n]*", [.dotMatchesLineSeparators])

// ------------------------------------------------------------- parted questions

/// Extract one lettered data-response question, parts (a) onwards, from a run of
/// pages. Used for three different things, because they are the same shape:
///
///   Papers 1 and 2, Section B  - Q6, parts (a) to (e), all compulsory.
///   Paper 3, Section A         - Q1, (a) to (c) compulsory, then (d) OR (e).
///   Paper 3, Section B         - Q2, same again.
///
/// Most papers print a consolidated list of all the parts on one page. Some do
/// not - Paper 2 June 2017 and June 2019 print each part above its own answer
/// space instead. Both layouts are handled by scanning every page in the range
/// for part openers and keeping the FIRST occurrence of each letter, which is
/// the consolidated list where one exists and the answer page where it does not.
///
/// `choiceLetters` names parts that are alternatives to each other. They are all
/// extracted - a student revising wants both - and share a choiceGroup so the UI
/// can say only one was sat.
///
/// `letters` is the full run of parts the question is expected to have. 9EC0
/// runs (a) to (e) everywhere; 8EC0 Section B runs (a) to (g), because AS keeps
/// its 20-mark essay choice inside Section B instead of splitting it out into a
/// Section C the way the A Level does.
func extractParts(
    pages: [String], from startIdx: Int, to endIdx: Int, question qnum: String,
    section: String, choiceLetters: [String], letters: [String] = ["a", "b", "c", "d", "e"],
    sources: Range<Int>? = nil, meta: PaperMeta, msPages: [String]
) -> ([QuestionOut], [String]) {
    var problems: [String] = []

    // The extract block a student must read. "Extract A" is normally its first
    // page; some Paper 3 sections label theirs C or D, so fall back to the first
    // page carrying any "Extract <letter>" and then to the section opener. On a
    // booklet paper the same search runs over the section's block in the
    // booklet instead, falling back to the block's heading page.
    let searchRange = sources ?? (startIdx..<endIdx)
    let extractPage =
        searchRange.first(where: { pages[$0].contains("Extract A") }).map { $0 + 1 }
        ?? searchRange.first(where: {
            rx("Extract [A-H]\\b").matches(pages[$0])
        }).map { $0 + 1 }
        ?? ((sources?.lowerBound ?? startIdx) + 1)

    // "(a) <text> (5)" — text is non-greedy up to the tariff in its own brackets.
    // The class is built from `letters` so an AS paper's (f) and (g) are seen
    // and an A Level paper's are still ignored.
    let partRe = rx(
        "\\(([\(letters.first ?? "a")-\(letters.last ?? "e")])\\)\\s*(.+?)\\s*\\((\\d{1,2})\\)",
        [.dotMatchesLineSeparators])

    var seen: [String: QuestionOut] = [:]

    for i in startIdx..<endIdx {
        var cleaned = stripFurniture(pages[i])
        if sources != nil {
            cleaned = bookletPreamble.stringByReplacingMatches(
                in: cleaned, range: NSRange(location: 0, length: (cleaned as NSString).length),
                withTemplate: " ")
        }
        for m in partRe.allMatches(cleaned) {
            guard let letter = m[1], let rawBody = m[2], let marksStr = m[3],
                let marks = Int(marksStr), seen[letter] == nil
            else { continue }

            // Section B keeps its citations on the extract pages, which are not
            // extracted, so this finds nothing on 9EC0 today. Applied anyway:
            // it costs one pass and means a paper that does print one inline
            // cannot reintroduce the problem.
            let cited = stripAttribution(normalise(rawBody))
            let body = cited.text
            // A match spanning a page break can swallow the next part; reject
            // bodies that still contain another part opener or a stray tariff.
            if body.isEmpty || body.count < 15 { continue }
            if rx("\\([a-e]\\)").matches(body) { continue }

            var notes: [String] = []
            var confidence = "high"
            if body.count > 600 {
                confidence = "low"
                notes.append("extracted text is unusually long; may span two parts")
            }

            let label = "\(qnum)(\(letter))"
            let hit = markSchemePage(msPages, question: qnum, part: letter)
            let ms = hit?.page
            if hit == nil {
                confidence = "low"
                notes.append("mark scheme page for \(label) could not be verified")
            } else if hit!.exact == false {
                notes.append(
                    "mark scheme heading for \(label) omits the question number; "
                        + "matched on the bare part label")
            }

            let group =
                choiceLetters.contains(letter)
                ? "\(meta.idStem)-q\(qnum)-choice" : nil

            seen[letter] = QuestionOut(
                id: "\(meta.idStem)-q\(qnum)\(letter)", section: section,
                questionNumber: label, parentQuestion: qnum, choiceGroup: group,
                marks: marks, questionText: body, sourceAttribution: cited.attribution,
                contextPage: extractPage,
                qpPage: i + 1, msPage: ms, msVerified: ms != nil,
                confidence: confidence, notes: notes)
        }
    }

    let out = letters.compactMap { seen[$0] }
    if out.count != letters.count {
        let missing = letters.filter { seen[$0] == nil }
        problems.append(
            "Q\(qnum): missing part(s) \(missing.joined(separator: ", "))")
    }
    return (out, problems)
}

/// Papers 1 and 2: Section B is a single data-response question, always Q6.
func extractSectionB(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    // On a booklet paper the booklet repeats "before answering Question 6", so
    // the search stops where the booklet starts.
    let booklet = sourceBooklet(pages)
    let questionPages = booklet.first?.page ?? pages.count

    guard
        let startIdx = (0..<questionPages).first(where: {
            pages[$0].contains("SECTION B") && beforeAnswering.matches(pages[$0])
        })
    else {
        return ([], ["Section B page not found"])
    }

    guard let qm = beforeAnswering.firstMatch(pages[startIdx]),
        let qnum = qm[1]
    else {
        return ([], ["Section B question number not found"])
    }

    // 9EC0 Section B ends where Section C begins. 8EC0 has no Section C - the
    // section runs to the end of the paper - and its last two parts are the
    // 20-mark either/or, which the A Level prints as Section C instead.
    let endIdx =
        meta.isAS
        ? questionPages
        : ((0..<questionPages).first(where: { pages[$0].contains("SECTION C") })
            ?? questionPages)

    return extractParts(
        pages: pages, from: startIdx, to: endIdx, question: qnum, section: "B",
        choiceLetters: meta.isAS ? ["f", "g"] : [],
        letters: meta.isAS
            ? ["a", "b", "c", "d", "e", "f", "g"] : ["a", "b", "c", "d", "e"],
        sources: bookletRange(booklet, section: "B", pageCount: pages.count),
        meta: meta, msPages: msPages)
}

// ------------------------------------------------------------------ paper 3

/// Paper 3 is two 50-mark case studies: Section A is Q1, Section B is Q2. Each
/// runs (a) to (c) compulsory then a choice of (d) or (e). Uniform across all
/// eight papers.
func extractPaper3(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    var out: [QuestionOut] = []
    var problems: [String] = []

    // A section is located by its instruction line, not by a "SECTION x"
    // heading. Paper 3 June 2024 prints no "SECTION B" heading above its second
    // case study at all — the words appear only in the "TOTAL FOR SECTION B"
    // line on the last page — so keying off the heading loses half that paper.
    // On a booklet paper the booklet repeats each instruction line, so the
    // search stops where the booklet starts.
    let booklet = sourceBooklet(pages)
    let questionPages = booklet.first?.page ?? pages.count
    var starts: [(page: Int, question: String)] = []
    for (i, page) in pages[0..<questionPages].enumerated() {
        guard let m = beforeAnswering.firstMatch(page), let n = m[1] else { continue }
        if starts.contains(where: { $0.question == n }) { continue }
        starts.append((i, n))
    }

    if starts.isEmpty {
        return ([], ["Paper 3: no section openers found"])
    }
    if starts.count != 2 {
        problems.append(
            "Paper 3: expected 2 sections, found \(starts.count) "
                + "(questions \(starts.map { $0.question }.joined(separator: ", ")))")
    }

    for (idx, start) in starts.enumerated() {
        let end = idx + 1 < starts.count ? starts[idx + 1].page : questionPages
        // Section A carries Q1 and Section B carries Q2 in all eight papers, but
        // the label is derived from position rather than assumed from the number.
        let section = idx == 0 ? "A" : "B"
        let (qs, ps) = extractParts(
            pages: pages, from: start.page, to: end, question: start.question,
            section: section, choiceLetters: ["d", "e"],
            sources: bookletRange(booklet, section: section, pageCount: pages.count),
            meta: meta, msPages: msPages)
        out += qs
        problems += ps
    }

    if out.count != 10 {
        problems.append("expected 10 Paper 3 questions, got \(out.count)")
    }
    return (out, problems)
}

// ------------------------------------------------------------ section A

// Edexcel A Papers 1 and 2, Section A, 9EC0 and 8EC0. Read from all 36
// papers, not assumed (review sheet phase-6-section-a.md, approved by Eliot
// 2026-11-24):
//
//   A Level  Q1-Q5, 5 marks each = 25.   AS  Q1-Q5, 4 marks each = 20.
//
// Every question has exactly one multiple-choice part - 1 mark, A-D answer
// boxes - beside its written parts. Phase 6 extracts the written parts only;
// the MCQs wait for Phase 7. A part is an MCQ if and only if it prints A-D
// boxes, never by its mark: AS sets 1-mark "Define the term" parts.
//
// Each card carries its question's opening stem, then every lead-in printed
// above it within the question, then its own text - all verbatim (decision
// 2A). A chart, table or diagram printed with the question is not reproduced:
// PDFKit returns its labels and cells as stray short lines, which keepProse()
// drops, and the card links to the question's first page instead.
// Sub-parts (i)/(ii) stay inside their lettered part, marks summed (decision 3).

/// Section A's candidate instructions, from the heading to the last sentence
/// every one of the 36 papers prints ("... include diagrams in your answers.").
let sectionAPreamble = rx("SECTION A\\b[\\s\\S]{0,600}?diagrams\\s+in\\s+your\\s+answers\\.")

/// Pearson's citation, bounded: no nested brackets, at most 400 characters.
/// The unbounded `attribution` is safe on one question's text, but Section A
/// is parsed as one stream, where a citation whose closing bracket PDFKit has
/// moved (Paper 2 June 2023 Q2) would run on through every balanced "(b)" and
/// "(4)" to the next citation. No URL is required, because Section A prints
/// citations without one ("(Source: adapted from 'Flower Struggles', Matthew
/// Wilson, ...)", "(Source: adapted from www.gov.uk/...)"); the colon within
/// the opening words - "(Source:", "(Source adapted from:" - is what no prose
/// bracket carries. Whatever survives is caught by the checks on the text.
let attributionA = rx("\\(\\s*Sources?\\b[^():]{0,30}:[^()]{0,400}?\\)")

/// A part label PDFKit has set on an answer option of the MCQ above it:
/// "(b) A 35 %" (AS Paper 1 June 2023), "(c) A maximum price of 0P1 per unit"
/// (AS Paper 1 June 2016), "(b) B A subsidy to coffee bean producers" (AS
/// Paper 1 June 2025). Moved only off A, B or C, and only when the next option
/// line is the next letter: a part whose own text begins "A manufacturer ..."
/// is followed by its own "A 0.15%", and a label on D followed by C (Paper 2
/// June 2022 2(a)) is an MCQ's own label on options read in reverse.
let gluedLabelA = rx("^\\s*\\(([a-h])\\)\\s+(([ABC])\\s+\\S.*)$")

/// Table cells the text layer sets between a part label and its own text, on
/// the label's line, where no reading rule can tell them apart: id -> the exact
/// leading text to remove. Each checked against the rendered page. A missing
/// prefix is a problem, so an entry cannot outlive the layout it describes.
///   AS Paper 2 June 2016 2(a): "(a) Italy Define the term ..." - "Italy" is
///   the last row label of the table above the part.
let cellLeaksA: [String: String] = [
    "edexcel-as-p2-2016-jun-q2a": "Italy ",
]

/// Diagram options labelled in pairs: "A B" above two diagrams, "C D" below.
let optionPairA = rx("^[A-D](?:\\s+[A-D])+$")

/// A tariff alone on its line.
let tariffLineA = rx("^\\(\\d{1,2}\\)$")

/// A tariff closing its line: "(4)".
let tariffA = rx("\\((\\d{1,2})\\)[ \\t]*$", [.anchorsMatchLines])

/// An answer-box line: "A level of demand pull inflation", "Option C", a bare
/// "D" under a diagram, "A B" above two diagram options.
let optionLineA = rx("^(?:Option\\s+)?([A-D])(?:\\s|$)")

/// "(i) consumers", "(ii) government." - a sub-part inside a lettered part.
let subPartA = rx("^\\((i{1,3}|iv)\\)\\s*(.*)$")

/// Words of two or more letters, for telling a sentence from a chart label.
func letterWords(_ s: String) -> Int {
    return s.split(separator: " ").filter { $0.filter { $0.isLetter }.count >= 2 }.count
}

/// Ends a sentence, looking past a closing quote or bracket: "price’." "(EU)."
func endsSentence(_ s: String) -> Bool {
    let t = s.reversed().drop(while: { "’”\"')".contains($0) })
    return t.first.map { ".?!:".contains($0) } ?? false
}

let functionWordsA: Set<String> = [
    "a", "an", "and", "as", "at", "between", "by", "for", "from", "in", "its", "of",
    "on", "or", "per", "than", "that", "the", "their", "to", "with",
]
func endsOnFunctionWord(_ s: String) -> Bool {
    return s.split(separator: " ").last.map { functionWordsA.contains($0.lowercased()) } ?? false
}

/// The prose in a run of Section A lines, with the figure text dropped.
///
/// What PDFKit returns between a question's sentences is the cell and label
/// text of whatever was printed there: "Year Quantity of UK new house builds",
/// "2016 134 612", "Price of / wheat / Supply / H / J". Printed prose is either
/// a full-width wrapped line or a line that ends a sentence, so a line is kept
/// when it is long, ends a sentence, or (inside an unfinished sentence) starts
/// lower case; anything else is dropped, and counted. Nothing is rewritten -
/// lines are kept whole or not at all.
///
/// `title`: the first line is the text on the question-number line, kept
/// whatever it is, because it is the question's opening as printed - for a
/// data question it is the chart's title ("UK real GDP, 2020-2022").
/// `open`: keep a sentence still unfinished at the end (a part's own text,
/// which runs up to its tariff: "... the amount spent ... by the EU / would be").
func keepProse(_ raw: String, title: Bool, open: Bool) -> (text: String, dropped: Int) {
    let lines = raw.components(separatedBy: .newlines)
        .map { $0.trimmingCharacters(in: .whitespaces) }
        .filter { !$0.isEmpty }
    var kept: [String] = []
    var para: [String] = []
    // The open run is one that must be kept even if no sentence end follows:
    // the question-number line, or a bullet item ("• Private dental treatment
    // £95–£700", AS Paper 1 June 2018), which prints without a full stop.
    var keepOpen = false
    var bulletNext = false
    var dropped = 0
    for (i, line) in lines.enumerated() {
        let long = line.count >= 45 && letterWords(line) >= 4
        let ends = endsSentence(line)
        if i == 0 && title {
            if ends || !long { kept.append(line) } else { para = [line]; keepOpen = true }
            continue
        }
        // PDFKit returns a bullet as a lone "•" line ahead of its item.
        if line == "•" {
            if keepOpen || !para.isEmpty { kept += para }
            para = []
            keepOpen = false
            bulletNext = true
            continue
        }
        if bulletNext {
            bulletNext = false
            if ends { kept.append("• " + line) } else { para = ["• " + line]; keepOpen = true }
            continue
        }
        // A data heading printed on its own line ("Statement 2", AS Paper 1
        // June 2024 Q4): kept, and the line above it with it - "Finland has
        // schools with an average class size of 19.6" prints no full stop.
        if rx("^Statement \\d+$").matches(line) {
            kept += para + [line]
            para = []
            keepOpen = false
            continue
        }
        // A line ending on a word no sentence ends with ("... seasonally
        // adjusted, from" / "2008 to 2015", Paper 2 June 2017) was wrapped, so
        // the next line continues it whatever it starts with.
        let wrapped = para.last.map { endsOnFunctionWord($0) } ?? false
        if ends && (!para.isEmpty || letterWords(line) >= 3) {
            kept += para + [line]
            para = []
            keepOpen = false
        } else if wrapped {
            para.append(line)
        } else if long {
            para.append(line)
        } else if !para.isEmpty, let f = line.first, f.isLowercase {
            para.append(line)
        } else {
            if keepOpen {
                kept += para
                para = []
                keepOpen = false
            } else if let l = para.last?.last, l.isNumber || "%£$€".contains(l) {
                // A long line cut off by figure text and ending on a figure
                // is a table row, not the start of a sentence: dropped rather
                // than glued to whatever sentence comes next.
                dropped += para.count
                para = []
            }
            dropped += 1
        }
    }
    if !para.isEmpty {
        if open || keepOpen { kept += para } else { dropped += para.count }
    }
    return (normalise(kept.joined(separator: "\n")), dropped)
}

func extractSectionA(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    var problems: [String] = []
    let questionCount = 5
    let perQuestion = meta.isAS ? 4 : 5

    guard let first = pages.firstIndex(where: { $0.contains("SECTION A") }) else {
        return ([], ["Section A heading not found"])
    }
    guard let last = (first..<pages.count).first(where: { pages[$0].contains("TOTAL FOR SECTION A") })
    else {
        return ([], ["no 'TOTAL FOR SECTION A' line"])
    }

    // The section's lines, furniture stripped, each with its page.
    var tagged: [(page: Int, line: String)] = []
    for i in first...last {
        var text = pages[i]
        if i == first {
            if let m = sectionAPreamble.firstMatch(in: text, range: NSRange(location: 0, length: (text as NSString).length)) {
                text = (text as NSString).substring(from: m.range.location + m.range.length)
            } else {
                problems.append("Section A preamble not recognised")
            }
        }
        if i == last, let r = text.range(of: "TOTAL FOR SECTION A") {
            text = String(text[..<r.lowerBound])
        }
        // The answer boxes are private-use glyphs (U+F0A2); a line of nothing
        // else would otherwise count as text and pin a stem to the wrong page.
        for raw in stripFurniture(text).components(separatedBy: .newlines) {
            let l = String(String.UnicodeScalarView(raw.unicodeScalars.filter { !(0xE000...0xF8FF).contains($0.value) }))
                .trimmingCharacters(in: .whitespaces)
            // The publication line some pages print at the foot ("1 D63211A
            // ©2020 Pearson Education Ltd.", AS Paper 2 October 2020).
            if l.contains("Pearson Education Ltd") { continue }
            if !l.isEmpty { tagged.append((i + 1, l)) }
        }
    }

    // A label glued to option A is moved to the first line after the options
    // - which may be on the next page. Reading order repaired; no word changes.
    var movedTo = Set<Int>()
    func optionLetter(_ l: String) -> String? { optionLineA.firstMatch(l)?[1] ?? nil }
    for i in tagged.indices {
        guard let m = gluedLabelA.firstMatch(tagged[i].line), let label = m[1], let rest = m[2],
            let on = m[3], let nextLetter = ["A": "B", "B": "C", "C": "D"][on]
        else { continue }
        var j = i + 1
        while j < tagged.count, tagged[j].line.first?.isLowercase == true { j += 1 }
        guard j < tagged.count, optionLetter(tagged[j].line) == nextLetter else { continue }
        guard let d = (j..<tagged.count).first(where: { optionLetter(tagged[$0].line) == "D" }) else { continue }
        var target = d + 1
        while target < tagged.count, tagged[target].line.first?.isLowercase == true { target += 1 }
        guard target < tagged.count else { continue }
        tagged[i].line = rest
        tagged[target].line = "(\(label)) " + tagged[target].line
        movedTo.insert(target)
    }

    // One stream, with the offset each line starts at so every match can be
    // traced back to its page.
    var stream = ""
    var lineStarts: [(offset: Int, page: Int, moved: Bool)] = []
    for (k, t) in tagged.enumerated() {
        lineStarts.append(((stream as NSString).length, t.page, movedTo.contains(k)))
        stream += t.line + "\n"
    }
    func lineAt(_ offset: Int) -> (offset: Int, page: Int, moved: Bool) {
        lineStarts.last(where: { $0.offset <= offset })!
    }
    func pageAt(_ offset: Int) -> Int { lineAt(offset).page }

    // Citations are blanked in place - same length, newlines kept - so every
    // offset above still holds, and remembered by position, so a part carries
    // only those printed above its own tariff.
    var units = Array(stream.utf16)
    var citations: [(offset: Int, text: String)] = []
    for m in attributionA.matches(in: stream, range: NSRange(location: 0, length: units.count)) {
        citations.append((m.range.location, normalise((stream as NSString).substring(with: m.range))))
        for k in m.range.location..<(m.range.location + m.range.length) where units[k] != 0x0A {
            units[k] = 0x20
        }
    }
    let ns = String(decoding: units, as: UTF16.self) as NSString
    func text(_ a: Int, _ b: Int) -> String { b > a ? ns.substring(with: NSRange(location: a, length: b - a)) : "" }
    func lines(_ s: String) -> [String] {
        s.components(separatedBy: .newlines).map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty }
    }

    let totals = rx("\\(Total for Question (\\d+) = (\\d+) marks\\)").matches(
        in: ns as String, range: NSRange(location: 0, length: ns.length))
    if totals.count != questionCount {
        problems.append("expected \(questionCount) questions, found \(totals.count) total lines")
    }

    var out: [QuestionOut] = []
    var segStart = 0
    for (qi, t) in totals.enumerated() {
        let qnum = ns.substring(with: t.range(at: 1))
        let printed = Int(ns.substring(with: t.range(at: 2)))!
        let segEnd = t.range.location
        defer { segStart = t.range.location + t.range.length }
        if qnum != String(qi + 1) { problems.append("question \(qi + 1) printed as \(qnum)") }
        if printed != perQuestion { problems.append("Q\(qnum): printed total \(printed), expected \(perQuestion)") }

        let seg = NSRange(location: segStart, length: segEnd - segStart)
        // A question number printed on a line of its own is taken out with the
        // page numbers by stripFurniture, and AS Paper 2 June 2019 has no "1"
        // in its text layer at all. The stem then starts where the question
        // does, and its first line is not assumed to be a title.
        let opener = rx("(?m)^[ \\t]*\(qnum)[ \\t]+(?=\\S)").firstMatch(in: ns as String, range: seg)
        let stemStart = opener.map { $0.range.location + $0.range.length } ?? segStart
        let openerAt = opener?.range.location ?? segStart

        // Part openers, in order from (a), each searched for after the last.
        var openers: [(letter: String, at: Int, end: Int)] = []
        var cursor = stemStart
        for letter in ["a", "b", "c", "d", "e", "f", "g", "h"] {
            let r = ns.range(of: "(\(letter))", options: [], range: NSRange(location: cursor, length: segEnd - cursor))
            if r.location == NSNotFound { break }
            openers.append((letter, r.location, r.location + r.length))
            cursor = r.location + r.length
        }
        if openers.isEmpty { problems.append("Q\(qnum): no parts found"); continue }

        struct Part { var letter: String; var at: Int; var marks: Int; var isMCQ: Bool
                      var body: String; var subs: [String]; var bodyEnd: Int; var after: Int; var dropped: Int
                      var notes: [String] }
        // Each label's region runs to the next label, and holds its tariffs.
        let regionEnds = openers.indices.map { $0 + 1 < openers.count ? openers[$0 + 1].at : segEnd }
        var tariffs = openers.indices.map {
            tariffA.matches(in: ns as String, range: NSRange(location: openers[$0].end, length: regionEnds[$0] - openers[$0].end))
        }
        let subLines = openers.indices.map {
            lines(text(openers[$0].end, regionEnds[$0])).filter { subPartA.matches($0) }
        }
        // A tariff can come out of the text layer away from its own label.
        // Re-homed only from a neighbour that holds more than its share, and
        // never from a part with sub-parts, whose extra tariffs are its own:
        //   ahead of the label - AS Paper 1 June 2017 Q1, "(3)" above the
        //     table and "(a)" below it: exactly one tariff between the
        //     previous region (or the question's start) and this label;
        //   after the next part - AS Paper 1 June 2017 Q2, "(a) ... (b) ...
        //     (1) (2)": the next region holds two and no sub-parts.
        var homed: [Int: String] = [:]
        for j in openers.indices where tariffs[j].isEmpty {
            let from = j == 0 ? stemStart : (tariffs[j - 1].last.map { $0.range.location + $0.range.length } ?? openers[j].at)
            let before = tariffA.matches(in: ns as String, range: NSRange(location: from, length: openers[j].at - from))
            if before.count == 1 {
                tariffs[j] = before
                homed[j] = "the text layer prints this part's tariff before its label"
            } else if j + 1 < openers.count, tariffs[j + 1].count >= 2, subLines[j + 1].isEmpty {
                tariffs[j] = [tariffs[j + 1].removeFirst()]
                homed[j] = "the text layer prints this part's tariff after the next part's text"
            }
        }

        var parts: [Part] = []
        for (j, o) in openers.enumerated() {
            let regionEnd = regionEnds[j]
            var notes: [String] = []
            if lineAt(o.at).moved {
                notes.append("the text layer sets this label on an option of the MCQ above; read from after that MCQ's options")
            }
            let marks = tariffs[j]
            guard !marks.isEmpty else {
                problems.append("Q\(qnum)(\(o.letter)): no tariff found")
                continue
            }
            // A re-homed tariff is not inside the region, so the text runs to
            // the next label.
            let inside = marks[0].range.location > o.end && marks[0].range.location < regionEnd
            let bodyEnd = inside ? marks[0].range.location : regionEnd
            let after = inside ? marks.last!.range.location + marks.last!.range.length : regionEnd
            if let h = homed[j] { notes.append(h) }
            let tariff = marks.reduce(0) { $0 + Int(ns.substring(with: $1.range(at: 1)))! }

            // An MCQ prints answer boxes B, C and D each opening a line. A is
            // not required: PDFKit can run it onto the end of the question
            // ("... circular flow of income? A Imports", Paper 2 June 2022), and
            // can return the four in reverse (D, C, B, A). Diagram options
            // labelled in pairs ("A B", "C D") count every letter of the pair.
            var letters = Set<String>()
            for l in lines(text(o.end, regionEnd)) {
                if optionPairA.matches(l) {
                    l.split(separator: " ").forEach { letters.insert(String($0)) }
                } else if let x = optionLetter(l) {
                    letters.insert(x)
                }
            }
            let isMCQ = ["B", "C", "D"].allSatisfy { letters.contains($0) }

            // Sub-part lines anywhere before the next label - AS Paper 2 June
            // 2019 5(b) prints its one tariff above (i) and (ii); the rest of
            // the text up to the FIRST tariff is the part's own wording.
            let subs = subLines[j]
            let ownRaw = lines(text(o.end, bodyEnd))
                .filter { !subPartA.matches($0) && !tariffLineA.matches($0) }.joined(separator: "\n")
            let own = keepProse(ownRaw, title: false, open: true)
            parts.append(Part(
                letter: o.letter, at: o.at, marks: tariff, isMCQ: isMCQ,
                body: own.text, subs: subs.map { normalise($0) }, bodyEnd: bodyEnd,
                after: after, dropped: own.dropped, notes: notes))
        }
        if parts.isEmpty { continue }

        // Stem, then the lead-in printed above each later part.
        let stem = keepProse(text(stemStart, openers[0].at), title: opener != nil, open: false)
        var leads: [String] = [stem.text]
        var dropped = [stem.dropped]
        for j in 1..<max(parts.count, 1) where j < parts.count {
            var between = lines(text(parts[j - 1].after, parts[j].at))
            if parts[j - 1].isMCQ {
                // The answer options of the MCQ above, and any wrapped
                // continuation of the last one, are not a lead-in.
                if let lastOpt = between.lastIndex(where: { optionLineA.matches($0) }) {
                    between = Array(between[(lastOpt + 1)...])
                    while let f = between.first?.first, f.isLowercase { between.removeFirst() }
                }
            }
            let lead = keepProse(between.joined(separator: "\n"), title: false, open: false)
            leads.append(lead.text)
            dropped.append(lead.dropped)
        }

        // Independent structure checks: one MCQ worth 1 mark, tariffs summing
        // to the printed total, letters running from (a) without a gap.
        let mcqs = parts.filter { $0.isMCQ }
        if mcqs.count != 1 {
            problems.append("Q\(qnum): \(mcqs.count) multiple-choice parts, expected 1 (\(mcqs.map { $0.letter }.joined()))")
        }
        for m in mcqs where m.marks != 1 { problems.append("Q\(qnum)(\(m.letter)): MCQ worth \(m.marks)") }
        let sum = parts.reduce(0) { $0 + $1.marks }
        if sum != printed { problems.append("Q\(qnum): tariffs sum to \(sum), paper prints \(printed)") }
        let run = "abcdefgh".prefix(parts.count).map { String($0) }
        if parts.map({ $0.letter }) != run { problems.append("Q\(qnum): parts are not a run from (a)") }

        // Without a printed number the question starts on the first line after
        // the previous question's total, not on the total's own line.
        let stemPage = opener != nil
            ? pageAt(openerAt)
            : (lineStarts.first(where: { $0.offset >= segStart })?.page ?? pageAt(segStart))
        for (j, p) in parts.enumerated() where !p.isMCQ {
            var notes = p.notes
            var confidence = "high"
            if opener == nil { notes.append("the question number is not in the text layer; the stem is read from the start of the question") }
            let carried = leads[0...j].filter { !$0.isEmpty }
            var body = p.body
            if let leak = cellLeaksA["\(meta.idStem)-q\(qnum)\(p.letter)"] {
                if body.hasPrefix(leak) {
                    body = String(body.dropFirst(leak.count))
                    notes.append("a table cell the text layer sets on the label's line is removed: '\(leak.trimmingCharacters(in: .whitespaces))'")
                } else {
                    problems.append("Q\(qnum)(\(p.letter)): expected table-cell leak '\(leak)' not found")
                }
            }
            if !p.subs.isEmpty {
                body += " " + p.subs.joined(separator: " ")
                notes.append("sub-parts \(p.subs.count == 2 ? "(i) and (ii)" : "(i)-(\(p.subs.count))") kept inside the part, marks summed")
            }
            if p.body.count < 15 {
                confidence = "low"
                notes.append("the part's own text is suspiciously short (\(p.body.count) chars)")
            }
            if leads[0].isEmpty { notes.append("no stem text found above the parts") }
            if j > 0 && leads[1...j].contains(where: { !$0.isEmpty }) {
                notes.append("lead-in printed between parts is included")
            }
            if dropped[0...min(j, dropped.count - 1)].reduce(0, +) + p.dropped > 0 {
                notes.append("figure or table text printed with the question is not reproduced; see the question paper")
            }
            let full = stripAttribution(normalise((carried + [body]).joined(separator: "\n")))
            if full.attribution != nil || full.text.contains("(Source") || full.text.contains("http")
                || full.text.contains("www.")
            {
                confidence = "low"
                notes.append("a citation or URL survived the strip")
            }
            let cites = citations.filter { $0.offset >= segStart && $0.offset < p.bodyEnd }.map { $0.text }
            let partPage = pageAt(p.at)
            let label = "\(qnum)(\(p.letter))"
            let hit = markSchemePage(msPages, question: qnum, part: p.letter)
            if hit == nil {
                confidence = "low"
                notes.append("mark scheme page for \(label) could not be verified")
            } else if hit!.exact == false {
                notes.append("mark scheme heading for \(label) omits the question number; matched on the bare part label")
            }
            out.append(QuestionOut(
                id: "\(meta.idStem)-q\(qnum)\(p.letter)", section: "A",
                questionNumber: label, parentQuestion: qnum, choiceGroup: nil,
                marks: p.marks, questionText: full.text,
                sourceAttribution: cites.isEmpty ? nil : cites.joined(separator: " "),
                // The question's opening page, where the stem and its data are
                // printed - only when the part itself is on a later page, so a
                // card never carries two links to the same page.
                contextPage: stemPage < partPage ? stemPage : nil,
                contextType: "question",
                qpPage: partPage, msPage: hit?.page, msVerified: hit != nil,
                confidence: confidence, notes: notes))
        }
    }
    return (out, problems)
}

// ------------------------------------------------------------ edexcel b

// Edexcel B (9EB0 A Level, 8EB0 AS). Read from all 37 papers, June 2016 to
// June 2025, not assumed from Edexcel A (review sheet phase-4-extraction.md,
// approved by Eliot 2026-11-16):
//
//   A Level P1, P2  Section A Q1 (a)-(h) = 60; Sections B and C one 20-mark
//                   question each (Q2, Q3), no parts.
//   A Level P3      Sections A and B, Q1 and Q2, each (a)-(d) = 50. The
//                   pre-release insert bound into two of the PDFs is skipped.
//   AS P1, P2       Q1 and Q2 (a)-(e) = 30 each; Section C one 20-mark Q3.
//
// Everything is compulsory, so choiceGroup is always null. A sentence printed
// above a part label (the lead-in) is part of the question and is kept,
// verbatim, at the start of questionText - as Edexcel A's Section C and AQA
// already carry their stems.

/// Candidate instructions between a section heading and its first question.
/// Removed, never rewritten. The "Read ... before answering" sentence can wrap
/// across a line (Paper 3 November 2021), hence the bounded any-character run.
let bInstructions: [NSRegularExpression] = [
    rx("Read\\b(?:(?!\\bRead\\b)[\\s\\S]){0,200}?before\\s+answering\\s+Question\\s+\\d+\\.?"),
    rx("(?m)^\\s*Answer ALL questions\\.?\\s*$"),
    rx("(?m)^\\s*SECTION [A-C](?: BEGINS ON THE NEXT PAGE\\.)?\\s*$"),
    rx("(?m)^\\s*Write your answers? in the spaces? provided\\.?\\s*$"),
    rx("(?m)^\\s*You are advised to spend[^\\n]*$"),
    rx("(?m)^\\s*\\(Total for Question \\d+ = \\d+ marks\\)\\s*$"),
    rx("(?m)^\\s*TOTAL FOR (?:SECTION [A-C]|PAPER) = \\d+ MARKS\\s*$"),
]

func stripInstructions(_ s: String) -> String {
    var out = s
    for r in bInstructions {
        out = r.stringByReplacingMatches(
            in: out, range: NSRange(location: 0, length: (out as NSString).length),
            withTemplate: " ")
    }
    return out
}

/// What 9EB0 / 8EB0 print, read from all 36 question papers with a text layer
/// (AS Paper 2 June 2019 is a scan). Used only to CHECK the derived structure:
/// the parts and tariffs themselves are read from the page.
struct BSection { let letter: String; let question: String; let parts: Int; let total: Int }
func expectedB(_ meta: PaperMeta) -> [BSection] {
    if meta.isAS {
        return [BSection(letter: "A", question: "1", parts: 5, total: 30),
                BSection(letter: "B", question: "2", parts: 5, total: 30),
                BSection(letter: "C", question: "3", parts: 0, total: 20)]
    }
    if meta.paper == 3 {
        return [BSection(letter: "A", question: "1", parts: 4, total: 50),
                BSection(letter: "B", question: "2", parts: 4, total: 50)]
    }
    return [BSection(letter: "A", question: "1", parts: 8, total: 60),
            BSection(letter: "B", question: "2", parts: 0, total: 20),
            BSection(letter: "C", question: "3", parts: 0, total: 20)]
}

let extractHeading = rx("(?m)^\\s*Extract [A-Z]\\s*$")

/// The page a student should open first: the first extract the section's own
/// instruction names ("extracts (D to F)" -> Extract D), found in the section's
/// pages or, on a booklet paper, in its booklet block.
func bContextPage(_ pages: [String], start: Int, range: Range<Int>) -> Int {
    if let m = rx("[Ee]xtracts?\\s*\\(?\\s*([A-Z])\\b").firstMatch(pages[start]), let l = m[1],
        let hit = range.first(where: { rx("(?m)^\\s*Extract \(l)\\b").matches(pages[$0]) })
    {
        return hit + 1
    }
    if let hit = range.first(where: { extractHeading.matches(pages[$0]) }) { return hit + 1 }
    return range.lowerBound + 1
}

func extractB(pages: [String], meta: PaperMeta, msPages: [String]) -> ([QuestionOut], [String]) {
    var out: [QuestionOut] = []
    var problems: [String] = []

    // Question pages end at the booklet (June 2025) or after "TOTAL FOR PAPER",
    // which keeps Paper 3's bound-in pre-release insert (June 2017, November
    // 2021) out of every search.
    let booklet = sourceBooklet(pages)
    var questionPages = booklet.first?.page ?? pages.count
    if let last = (0..<questionPages).first(where: { pages[$0].contains("TOTAL FOR PAPER") }) {
        questionPages = min(questionPages, last + 1)
    }

    var starts: [(page: Int, question: String)] = []
    for i in 0..<questionPages {
        guard let m = beforeAnswering.firstMatch(pages[i]), let n = m[1] else { continue }
        if !starts.contains(where: { $0.question == n }) { starts.append((i, n)) }
    }
    if !pages[0..<questionPages].contains(where: { $0.contains("Answer ALL questions") }) {
        problems.append("no 'Answer ALL questions' instruction")
    }
    if pages[0..<questionPages].contains(where: { rx("(?m)^\\s*(EITHER|OR)\\s*$").matches($0) }) {
        problems.append("an EITHER/OR choice was printed; 9EB0/8EB0 should have none")
    }

    let expected = expectedB(meta)
    if starts.map({ $0.question }) != expected.map({ $0.question }) {
        problems.append(
            "expected questions \(expected.map { $0.question }.joined(separator: ",")), "
                + "found \(starts.map { $0.question }.joined(separator: ","))")
    }

    for (idx, start) in starts.enumerated() {
        let qnum = start.question
        let next = idx + 1 < starts.count ? starts[idx + 1].page : questionPages
        let totalRe = rx("\\(Total for Question \(qnum) = (\\d+) marks\\)")
        let totalPage = (start.page..<next).first(where: { totalRe.matches(pages[$0]) })
        let total = totalPage.flatMap { totalRe.firstMatch(pages[$0])?[1] }.flatMap { Int($0) }
        let end = totalPage.map { $0 + 1 } ?? next

        // Section letter as printed on the opener page; position only as a fallback.
        let printed = rx("(?m)^\\s*SECTION ([A-C])\\s*$").firstMatch(pages[start.page])?[1]
        let section = printed ?? ["A", "B", "C"][min(idx, 2)]
        if printed == nil { problems.append("Q\(qnum): no SECTION heading on its opener page; labelled \(section) by position") }

        // The extract named in the section's own instruction, looked for in the
        // section's booklet block; on a booklet paper that prints no block
        // heading for this section (Paper 1 June 2025 has none for Section B,
        // so Extract G sits under Section A's), in the whole booklet; and on
        // an older paper, in the section's own pages.
        let sources = bookletRange(booklet, section: section, pageCount: pages.count)
        let ctxRange = sources ?? (booklet.isEmpty ? start.page..<end : booklet[0].page..<pages.count)
        let ctx = bContextPage(pages, start: start.page, range: ctxRange)

        let partRe = rx("\\(([a-h])\\)\\s*(.+?)\\s*\\((\\d{1,2})\\)", [.dotMatchesLineSeparators])
        var parts: [QuestionOut] = []
        var seen = Set<String>()

        for i in start.page..<end {
            let cleaned = stripInstructions(stripFurniture(pages[i]))
            let ns = cleaned as NSString
            var cursor = 0
            for m in partRe.matches(in: cleaned, range: NSRange(location: 0, length: ns.length)) {
                let letter = ns.substring(with: m.range(at: 1))
                let rawBody = ns.substring(with: m.range(at: 2))
                let marks = Int(ns.substring(with: m.range(at: 3)))!
                // Text printed above the part label on the same page: the
                // lead-in ("New Balance operates in a competitive market.").
                // Part of the question as printed, so kept, verbatim.
                var segment = ns.substring(with: NSRange(location: cursor, length: m.range.location - cursor))
                cursor = m.range.location + m.range.length
                var notes: [String] = []
                var confidence = "high"
                // Where the question number is printed, the lead-in starts
                // after it ("1 Estimated global sales ... (a) Using ...") -
                // which also stops an extract sharing the page being swallowed.
                let seg = segment as NSString
                let numLine = rx("(?m)^[ \\t]*\(qnum)(?:[ \\t]+|$)").matches(
                    in: segment, range: NSRange(location: 0, length: seg.length)).last
                if let n = numLine {
                    segment = seg.substring(from: n.range.location + n.range.length)
                } else if extractHeading.matches(segment) {
                    segment = ""
                    confidence = "low"
                    notes.append("part shares a page with an extract and no question number anchors a lead-in; check the page")
                }
                // A figure printed inside the question (P2 June 2022 1(b)): its
                // cells flatten into nonsense, so the text starts after its label
                // and the card's question-paper link carries the figure.
                let figs = rx("(?m)^[ \\t]*Figure \\d+[ \\t]*$").matches(
                    in: segment, range: NSRange(location: 0, length: (segment as NSString).length))
                if let f = figs.last {
                    segment = (segment as NSString).substring(from: f.range.location + f.range.length)
                    notes.append("a figure printed on the question page is not reproduced; see the question paper page")
                }
                let lead = normalise(segment)
                guard !seen.contains(letter) else { continue }
                let body = normalise(rawBody)
                if body.count < 15 || rx("\\([a-h]\\)").matches(body) { continue }
                seen.insert(letter)

                if !lead.isEmpty {
                    notes.append("lead-in printed above the part label is included")
                    if lead.count > 400 || lead.contains("©") {
                        confidence = "low"
                        notes.append("lead-in may contain extract text")
                    }
                }
                let cited = stripAttribution(lead.isEmpty ? body : lead + " " + body)
                let hit = markSchemePage(msPages, question: qnum, part: letter, bScheme: true)
                if hit == nil { confidence = "low"; notes.append("mark scheme page for \(qnum)(\(letter)) could not be verified") }
                parts.append(QuestionOut(
                    id: "\(meta.idStem)-q\(qnum)\(letter)", section: section,
                    questionNumber: "\(qnum)(\(letter))", parentQuestion: qnum, choiceGroup: nil,
                    marks: marks, questionText: cited.text, sourceAttribution: cited.attribution,
                    contextPage: ctx, qpPage: i + 1, msPage: hit?.page, msVerified: hit != nil,
                    confidence: confidence, notes: notes))
            }
        }

        if parts.isEmpty {
            // A single extended response: "2 Evaluate ... (20)", or with a
            // printed stem first: "3 The UK government intervenes ... Evaluate ... (20)".
            let single = rx("(?:^|\\n)\\s*\(qnum)\\s+(\\S[\\s\\S]*?)\\s*\\((\\d{1,2})\\)")
            var found: QuestionOut? = nil
            for i in start.page..<end where !extractHeading.matches(pages[i]) {
                let cleaned = stripInstructions(stripFurniture(pages[i]))
                guard let m = single.firstMatch(cleaned), let raw = m[1], let mk = m[2].flatMap({ Int($0) })
                else { continue }
                let cited = stripAttribution(normalise(raw))
                var notes: [String] = []
                var confidence = "high"
                if cited.text.count < 40 { confidence = "low"; notes.append("extracted text is suspiciously short") }
                let hit = markSchemePage(msPages, question: qnum, part: nil, bScheme: true)
                if hit == nil { confidence = "low"; notes.append("mark scheme page for Q\(qnum) could not be verified") }
                found = QuestionOut(
                    id: "\(meta.idStem)-q\(qnum)", section: section, questionNumber: qnum,
                    parentQuestion: nil, choiceGroup: nil, marks: mk, questionText: cited.text,
                    sourceAttribution: cited.attribution, contextPage: ctx, qpPage: i + 1,
                    msPage: hit?.page, msVerified: hit != nil, confidence: confidence, notes: notes)
                break
            }
            if let f = found { parts = [f] } else { problems.append("Q\(qnum): question text not found") }
        }

        // Independent checks: tariffs sum to the printed total, letters run
        // from (a) without a gap, and the shape matches what B prints.
        let sum = parts.reduce(0) { $0 + $1.marks }
        if let t = total, t != sum { problems.append("Q\(qnum): tariffs sum to \(sum), paper prints \(t)") }
        if total == nil { problems.append("Q\(qnum): no '(Total for Question \(qnum) = N marks)' line") }
        let letters = parts.compactMap { $0.parentQuestion == nil ? nil : String($0.questionNumber.dropFirst(qnum.count + 1).prefix(1)) }
        let run = "abcdefgh".prefix(letters.count).map { String($0) }
        if letters != run { problems.append("Q\(qnum): parts \(letters.joined()) are not a run from (a)") }
        if let e = expected.first(where: { $0.question == qnum }) {
            if e.letter != section { problems.append("Q\(qnum): printed section \(section), expected \(e.letter)") }
            if e.parts != letters.count { problems.append("Q\(qnum): \(letters.count) parts, expected \(e.parts)") }
            if e.total != sum { problems.append("Q\(qnum): \(sum) marks, expected \(e.total)") }
        }
        out += parts
    }
    return (out, problems)
}

// ------------------------------------------------------------------ emit

func jsonEscape(_ s: String) -> String {
    var o = ""
    for c in s.unicodeScalars {
        switch c {
        case "\"": o += "\\\""
        case "\\": o += "\\\\"
        case "\n": o += "\\n"
        case "\r": o += "\\r"
        case "\t": o += "\\t"
        default:
            if c.value < 0x20 {
                o += String(format: "\\u%04x", c.value)
            } else {
                o.unicodeScalars.append(c)
            }
        }
    }
    return o
}

func urlFor(_ path: String) -> String {
    guard let r = path.range(of: "past-papers/") else { return path }
    return "/" + String(path[r.lowerBound...])
}

func emit(meta: PaperMeta, questions: [QuestionOut], problems: [String]) -> String {
    let qpUrl = urlFor(meta.qpPath)
    let msUrl = urlFor(meta.msPath)

    var lines: [String] = []
    lines.append("{")
    lines.append("  \"qualification\": \"\(jsonEscape(meta.qualification))\",")
    lines.append("  \"board\": \"\(meta.board)\",")
    lines.append("  \"boardName\": \"\(meta.boardName)\",")
    lines.append("  \"level\": \"\(meta.level)\",")
    lines.append("  \"paper\": \(meta.paper),")
    lines.append("  \"paperName\": \"\(jsonEscape(meta.paperName))\",")
    lines.append("  \"year\": \(meta.year),")
    lines.append("  \"series\": \"\(meta.series)\",")
    lines.append("  \"seriesSlug\": \"\(meta.seriesSlug)\",")
    lines.append("  \"questionPaperUrl\": \"\(jsonEscape(qpUrl))\",")
    lines.append("  \"markSchemeUrl\": \"\(jsonEscape(msUrl))\",")
    lines.append(
        "  \"problems\": [\(problems.map { "\"\(jsonEscape($0))\"" }.joined(separator: ", "))],")
    lines.append("  \"questions\": [")

    for (i, q) in questions.enumerated() {
        var f: [String] = []
        f.append("      \"id\": \"\(jsonEscape(q.id))\"")
        f.append("      \"section\": \"\(q.section)\"")
        f.append("      \"questionNumber\": \"\(jsonEscape(q.questionNumber))\"")
        f.append(
            "      \"parentQuestion\": "
                + (q.parentQuestion.map { "\"\($0)\"" } ?? "null"))
        f.append("      \"choiceGroup\": " + (q.choiceGroup.map { "\"\($0)\"" } ?? "null"))
        f.append("      \"marks\": \(q.marks)")
        f.append("      \"questionText\": \"\(jsonEscape(q.questionText))\"")
        // Omitted entirely when there is no citation, so the 420 questions that
        // never had one keep the shape they already have on disk.
        if let attr = q.sourceAttribution {
            f.append("      \"sourceAttribution\": \"\(jsonEscape(attr))\"")
        }
        if let cp = q.contextPage, q.contextType == "question" {
            // Wording approved by Eliot, 2026-11-24 (phase-6 Q4).
            f.append(
                "      \"context\": { \"type\": \"question\", "
                    + "\"label\": \"Question \(q.parentQuestion ?? q.questionNumber) as printed\", "
                    + "\"pdfUrl\": \"\(jsonEscape(qpUrl))\", \"page\": \(cp) }")
        } else if let cp = q.contextPage {
            f.append(
                "      \"context\": { \"type\": \"extracts\", "
                    + "\"label\": \"Extracts and figures for Question \(q.parentQuestion ?? q.questionNumber)\", "
                    + "\"pdfUrl\": \"\(jsonEscape(qpUrl))\", \"page\": \(cp) }")
        } else {
            f.append("      \"context\": null")
        }
        f.append(
            "      \"questionPaper\": { \"pdfUrl\": \"\(jsonEscape(qpUrl))\", "
                + "\"page\": \(q.qpPage) }")
        if let ms = q.msPage {
            f.append(
                "      \"markScheme\": { \"pdfUrl\": \"\(jsonEscape(msUrl))\", "
                    + "\"page\": \(ms), \"verified\": \(q.msVerified) }")
        } else {
            f.append("      \"markScheme\": null")
        }
        f.append("      \"modelAnswer\": null")
        f.append("      \"extractionConfidence\": \"\(q.confidence)\"")
        f.append(
            "      \"extractionNotes\": [\(q.notes.map { "\"\(jsonEscape($0))\"" }.joined(separator: ", "))]"
        )
        lines.append("    {")
        lines.append(f.joined(separator: ",\n"))
        lines.append("    }" + (i == questions.count - 1 ? "" : ","))
    }

    lines.append("  ]")
    lines.append("}")
    return lines.joined(separator: "\n") + "\n"
}

// ------------------------------------------------------------------ main

func pageTexts(_ path: String) -> [String]? {
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else { return nil }
    return (0..<doc.pageCount).map { doc.page(at: $0)?.string ?? "" }
}

/// Where the reviewed OCR transcript for an image-only question paper lives:
/// past-paper-questions-data/ocr/<the PDF's name>.txt. See ocr_pdf_pages.swift.
func transcriptPath(_ qpPath: String) -> String {
    let name = ((qpPath as NSString).lastPathComponent as NSString).deletingPathExtension
    return "past-paper-questions-data/ocr/\(name).txt"
}

/// The pages of a reviewed transcript: everything under each
/// "=== PAGE n ===" marker; the header above the first marker is ignored.
/// Returns nil if the file is missing or its page count disagrees with the PDF.
func transcriptPages(_ path: String, expected: Int) -> [String]? {
    guard let raw = try? String(contentsOfFile: path, encoding: .utf8) else { return nil }
    var pages: [String] = []
    for line in raw.components(separatedBy: "\n") {
        if line.hasPrefix("=================== PAGE ") {
            pages.append("")
        } else if !pages.isEmpty {
            pages[pages.count - 1] += line + "\n"
        }
    }
    return pages.count == expected ? pages : nil
}

let args = Array(CommandLine.arguments.dropFirst())
guard !args.isEmpty else {
    FileHandle.standardError.write(
        "usage: swift scripts/extract_past_paper_questions.swift <question-paper.pdf> ...\n"
            .data(using: .utf8)!)
    exit(2)
}

// Two directories, because both qualifications have a Paper 1 in the same
// series and "p1-june-2017.json" would otherwise mean two different papers.
let outDirs = [
    "a-level": URL(fileURLWithPath: "past-paper-questions-data/edexcel-a"),
    "as-level": URL(fileURLWithPath: "past-paper-questions-data/edexcel-a-as"),
]
for dir in outDirs.values {
    try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
}

var exitCode: Int32 = 0

for path in args {
    // An Edexcel B filename also matches the Edexcel A pattern, and used to be
    // written into edexcel-a/ as if it were 9EC0. Route B first.
    let isBFile = (path as NSString).lastPathComponent.hasPrefix("edexcel-b-")
    guard let meta = isBFile ? parseMetaB(path) : parseMeta(path) else {
        FileHandle.standardError.write("SKIP (unparseable name): \(path)\n".data(using: .utf8)!)
        exitCode = 1
        continue
    }
    guard var qpPages = pageTexts(meta.qpPath) else {
        FileHandle.standardError.write("FAIL (cannot open QP): \(path)\n".data(using: .utf8)!)
        exitCode = 1
        continue
    }
    // A question paper with no text layer at all (one today: Edexcel B AS
    // Paper 2 June 2019, a scan) is read from its reviewed OCR transcript.
    // Without one it fails loudly rather than writing an empty paper.
    var transcript: String? = nil
    if qpPages.allSatisfy({ $0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }) {
        let t = transcriptPath(meta.qpPath)
        guard let ocr = transcriptPages(t, expected: qpPages.count) else {
            FileHandle.standardError.write(
                ("FAIL (no text layer, and no transcript with \(qpPages.count) pages at \(t); "
                    + "see scripts/ocr_pdf_pages.swift): \(path)\n").data(using: .utf8)!)
            exitCode = 1
            continue
        }
        qpPages = ocr
        transcript = t
    }
    guard let msPages = pageTexts(meta.msPath) else {
        FileHandle.standardError.write(
            "FAIL (cannot open MS): \(meta.msPath)\n".data(using: .utf8)!)
        exitCode = 1
        continue
    }

    var questions: [QuestionOut] = []
    var problems: [String] = []

    if meta.isB {
        (questions, problems) = extractB(pages: qpPages, meta: meta, msPages: msPages)
    } else if meta.paper == 3 {
        // Paper 3 has no Section C and its sections mean something different,
        // which is why `section` is a free string on the record rather than an
        // enum shared with Papers 1 and 2.
        (questions, problems) = extractPaper3(
            pages: qpPages, meta: meta, msPages: msPages)
    } else if meta.isAS {
        // 8EC0 has no Section C at all. Its Section B carries the whole of the
        // paper bar Section A: Q6(a) to (g), 60 of the 80 marks.
        let (a, aProblems) = extractSectionA(pages: qpPages, meta: meta, msPages: msPages)
        let (b, bProblems) = extractSectionB(pages: qpPages, meta: meta, msPages: msPages)
        questions = a + b
        problems = aProblems + bProblems
    } else {
        let (a, aProblems) = extractSectionA(pages: qpPages, meta: meta, msPages: msPages)
        let (b, bProblems) = extractSectionB(pages: qpPages, meta: meta, msPages: msPages)
        let (c, cProblems) = extractSectionC(pages: qpPages, meta: meta, msPages: msPages)
        questions = a + b + c
        problems = aProblems + bProblems + cProblems
    }

    if let t = transcript {
        for i in questions.indices {
            questions[i].notes.append(
                "the question paper is an image-only scan; text read from the reviewed OCR transcript \(t)")
        }
    }

    let name = "p\(meta.paper)-\(meta.seriesSlug).json"
    let dir = meta.isB ? URL(fileURLWithPath: "past-paper-questions-data/\(meta.outDir)") : outDirs[meta.level]!
    try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
    let dest = dir.appendingPathComponent(name)
    try! emit(meta: meta, questions: questions, problems: problems)
        .write(to: dest, atomically: true, encoding: .utf8)

    let low = questions.filter { $0.confidence != "high" }.count
    let unver = questions.filter { !$0.msVerified }.count
    var summary = "\(name): \(questions.count) questions"
    if low > 0 { summary += ", \(low) low-confidence" }
    if unver > 0 { summary += ", \(unver) unverified MS" }
    if !problems.isEmpty { summary += ", PROBLEMS: \(problems.joined(separator: "; "))" }
    FileHandle.standardError.write((summary + "\n").data(using: .utf8)!)
    if !problems.isEmpty || low > 0 { exitCode = 1 }
}

exit(exitCode)
