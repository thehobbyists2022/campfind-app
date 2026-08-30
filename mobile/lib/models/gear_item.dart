class GearItem {
  final String id;
  final String name;
  final String category;
  final String price;
  final String rating;
  final String badge;
  final String icon;
  final String reason;
  final String searchQuery;

  const GearItem({
    required this.id,
    required this.name,
    required this.category,
    required this.price,
    required this.rating,
    required this.badge,
    required this.icon,
    required this.reason,
    required this.searchQuery,
  });

  String get amazonUrl {
    const affiliateTag = 'campfindgear-20';
    final encodedQuery = Uri.encodeComponent(searchQuery.isNotEmpty ? searchQuery : name);
    return 'https://www.amazon.com/s?k=$encodedQuery&tag=$affiliateTag';
  }
}
