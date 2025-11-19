# QuickSpend - Implementation Notes

## 📐 Архитектура

### MVVM Pattern

```
┌─────────────────────────────────────────┐
│           QuickSpendApp.swift           │
│   (Entry point, ModelContainer setup)  │
└────────────┬────────────────────────────┘
             │
             ├─────────────────────────────┐
             │                             │
┌────────────▼───────────┐   ┌─────────────▼──────────┐
│      ContentView       │   │   BudgetViewModel      │
│  (Main UI + Charts)    │◄──┤  (Business Logic)      │
└────────┬───────────────┘   └─────────┬──────────────┘
         │                             │
         │                             │
┌────────▼───────────┐                 │
│     InputView      │                 │
│  (Quick Input UI)  │─────────────────┘
└────────┬───────────┘
         │
         │
┌────────▼───────────┐
│   InputParser      │
│  (Text Parsing)    │
└────────────────────┘
```

### Data Flow

```
User Input "500 кофе"
     │
     ├─► InputView
     │      │
     │      ├─► InputParser.parse()
     │      │      │
     │      │      └─► Returns: ParsedInput(amount: 500, category: "кофе")
     │      │
     │      └─► BudgetViewModel.submitTransaction()
     │             │
     │             ├─► Find/Create Category
     │             │      │
     │             │      └─► CategoryIconMapper.icon(for: "кофе")
     │             │             └─► Returns: "cup.and.saucer.fill"
     │             │
     │             └─► Create Transaction
     │                    │
     │                    └─► Save to SwiftData
     │
     └─► ContentView updates automatically (SwiftUI + @Query)
            │
            └─► Chart refreshes with new data
```

## 🔍 InputParser Logic

### Regex Pattern

```swift
let numberPattern = #"(\d+(?:[.,]\d+)?)"#
```

**Разбор:**
- `\d+` - одна или больше цифр
- `(?:[.,]\d+)?` - опциональная десятичная часть с точкой или запятой

### Parsing Flow

```
Input: "1200 еда бизнес ланч"
       │
       ├─► Step 1: Find first number
       │   Result: "1200" at position 0-3
       │
       ├─► Step 2: Extract amount
       │   Result: 1200.0
       │
       ├─► Step 3: Get remaining text
       │   Result: "еда бизнес ланч"
       │
       ├─► Step 4: Split by spaces
       │   Result: ["еда", "бизнес", "ланч"]
       │
       ├─► Step 5: First word = category
       │   Result: "еда"
       │
       └─► Step 6: Rest = note
           Result: "бизнес ланч"

Final: ParsedInput(amount: 1200.0, categoryName: "еда", note: "бизнес ланч")
```

## 🎨 Category Icon Mapping

### Logic Flow

```swift
CategoryIconMapper.icon(for: "кофе")
     │
     ├─► Lowercase: "кофе"
     │
     ├─► Check patterns:
     │   ├─ Contains "кофе" or "coffee"? ✅
     │   │  └─► Return "cup.and.saucer.fill"
     │   │
     │   ├─ Contains "еда" or "food"?
     │   │  └─► Return "fork.knife"
     │   │
     │   ├─ Contains "такси" or "taxi"?
     │   │  └─► Return "car.fill"
     │   │
     │   └─ ... (other patterns)
     │
     └─► Default: "cart"
```

## 💾 SwiftData Models

### Relationships

```
Category (1) ────── (*) Transaction
    │                       │
    ├─ name (unique)        ├─ amount: Double
    ├─ icon: String         ├─ date: Date
    └─ colorHex: String     ├─ note: String?
                            └─ category: Category?
```

### Cascade Delete

```
Delete Category
    │
    └─► deleteRule: .cascade
           │
           └─► All related Transactions are deleted automatically
```

## 📊 Chart Data Aggregation

### Monthly Totals by Category

```swift
transactions
    │
    ├─► Filter: Current month only
    │      │
    │      └─► Filter by date.month == Date().month
    │
    ├─► Group by category
    │      │
    │      └─► Dictionary<CategoryName, TotalAmount>
    │
    └─► Sort by amount (descending)
           │
           └─► [(category: "Еда", amount: 5000),
                (category: "Такси", amount: 2000),
                ...]
```

## 🎯 Key Features

### 1. Smart Parsing

✅ **Supports:**
- Integer amounts: `500 кофе`
- Decimal amounts: `99.50 такси`
- Comma separator: `150,75 еда`
- Multi-word notes: `1200 еда бизнес ланч`
- English & Russian: `300 Coffee morning espresso`

❌ **Limitations:**
- Only first number is recognized
- Category must be a single word
- Note can be multiple words

### 2. Auto Category Icons

📌 **Categories mapped:**
- Food & Drinks: кофе, еда, ресторан, продукты
- Transport: такси, транспорт, метро, бензин
- Entertainment: развлечения, кино, игры
- Shopping: покупки, одежда, техника
- Health: здоровье, аптека, спорт
- Bills: счета, интернет, телефон
- Education: образование
- Home: дом
- Beauty: красота
- Gifts: подарки

### 3. Live Validation

```
Input: "5" → ❌ (not submitted yet)
Input: "50" → ✅ Shows: "→ $50 · Uncategorized"
Input: "500 к" → ✅ Shows: "→ $500 · к"
Input: "500 кофе" → ✅ Shows: "→ $500 · кофе"
```

## 🧪 Testing Strategy

### Unit Tests (InputParserTests)

```swift
InputParserTests.runTests()
```

**Coverage:**
- ✅ Amount only
- ✅ Amount + Category
- ✅ Amount + Category + Note
- ✅ Decimal amounts
- ✅ Comma separator
- ✅ Complex notes
- ✅ English input
- ✅ Large amounts
- ✅ Amount in middle of text

### Manual Testing Scenarios

1. **Empty input** → Should not crash
2. **Invalid input (no numbers)** → Should show invalid state
3. **Very long note** → Should not overflow UI
4. **Duplicate categories** → Should reuse existing category
5. **Delete transaction** → Should update totals immediately
6. **Month change** → Should show $0 for new month

## 🚀 Performance Considerations

### SwiftData Queries

```swift
@Query(sort: \Transaction.date, order: .reverse)
```

- ✅ Sorted at database level (fast)
- ✅ Automatic updates via @Query
- ✅ No manual refreshing needed

### Chart Performance

```swift
Chart(categoryData, id: \.category) { ... }
```

- ✅ Only processes current month data
- ✅ Pre-aggregated in ViewModel
- ✅ Efficient SectorMark rendering

## 🎨 UI/UX Details

### Animations (Future)

```swift
.transition(.asymmetric(
    insertion: .move(edge: .top).combined(with: .opacity),
    removal: .move(edge: .leading).combined(with: .opacity)
))
```

### Keyboard Shortcuts

- `Cmd+N` → Focus input field
- `Enter` → Submit transaction
- `Escape` → Clear input (future)

### Accessibility

- ✅ VoiceOver labels on all icons
- ✅ Keyboard navigation
- ✅ Dynamic Type support (future)

## 📱 macOS Integration

### Window Management

```swift
.frame(minWidth: 600, minHeight: 700)
```

- Minimum size enforced
- Resizable window
- Compact by default

### Menu Bar Commands

```swift
.commands {
    CommandGroup(replacing: .newItem) {
        Button("New Transaction") { ... }
            .keyboardShortcut("n", modifiers: .command)
    }
}
```

## 🔮 Future Enhancements

### Phase 3: Enhanced UI
- [ ] Add transaction animations
- [ ] Sound effects on submit
- [ ] Better empty states
- [ ] Loading indicators

### Phase 4: Advanced Features
- [ ] Date range filters
- [ ] Search transactions
- [ ] Export to CSV/Excel
- [ ] Budget limits & alerts
- [ ] Recurring transactions
- [ ] Multiple currencies
- [ ] iCloud sync

### Phase 5: Polish
- [ ] App icon
- [ ] Menu bar widget
- [ ] Spotlight integration
- [ ] Share extension
- [ ] Widgets for macOS

## 🐛 Known Issues

1. **SwiftData in Preview** - Previews may not work without mock data
2. **Regex edge cases** - Numbers in category names might confuse parser
3. **Category uniqueness** - Case-sensitive (кофе ≠ Кофе)

## 💡 Tips for Development

### Debugging SwiftData

```swift
// Print all transactions
let descriptor = FetchDescriptor<Transaction>()
let all = try? modelContext.fetch(descriptor)
print("Total transactions: \(all?.count ?? 0)")
```

### Testing Regex

```swift
// Test in Swift Playground
let pattern = #"(\d+(?:[.,]\d+)?)"#
let regex = try! NSRegularExpression(pattern: pattern)
let text = "500 кофе"
if let match = regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)) {
    print("Found: \(text[Range(match.range, in: text)!])")
}
```

### Custom SF Symbols

Open SF Symbols app to browse:
```bash
open -a "SF Symbols"
```

---

**Happy Coding!** 🚀
