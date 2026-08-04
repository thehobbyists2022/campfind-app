import 'package:flutter/material.dart';
import '../models/camp_model.dart';

class CampCard extends StatelessWidget {
  final Camp camp;
  final bool isFavorite;
  final VoidCallback onFavoriteTap;
  final VoidCallback onTap;
  final VoidCallback onCompareTap;
  final bool isSelectedForCompare;

  const CampCard({
    Key? key,
    required this.camp,
    required this.isFavorite,
    required this.onFavoriteTap,
    required this.onTap,
    required this.onCompareTap,
    this.isSelectedForCompare = false,
  }) : super(key: key);

  Color _getThemeColor(String theme) {
    switch (theme.toLowerCase()) {
      case 'stem':
        return const Color(0xFF4ECDC4);
      case 'sports':
        return const Color(0xFFFF6B6B);
      case 'arts':
        return const Color(0xFF9B59B6);
      case 'outdoor':
        return const Color(0xFF2ECC71);
      case 'academic':
        return const Color(0xFFF39C12);
      default:
        return const Color(0xFF3498DB);
    }
  }

  @override
  Widget build(BuildContext context) {
    final themeColor = _getThemeColor(camp.theme);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF2C3E50).withOpacity(0.08),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
        border: isSelectedForCompare
            ? Border.all(color: const Color(0xFFFF6B6B), width: 2)
            : Border.all(color: Colors.grey.shade200),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Row: ACA Badge & Theme Tag & Favorite Button
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: themeColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.stars_rounded, size: 14, color: themeColor),
                          const SizedBox(width: 4),
                          Text(
                            camp.theme.toUpperCase(),
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: themeColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    if (camp.acaVerified)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8F5E9),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.verified, size: 12, color: Color(0xFF2E7D32)),
                            SizedBox(width: 3),
                            Text(
                              'ACA Verified',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF2E7D32),
                              ),
                            ),
                          ],
                        ),
                      )
                    else if (camp.unverified)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF3C7),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.help_outline, size: 12, color: Color(0xFFB45309)),
                            SizedBox(width: 3),
                            Text(
                              'Unverified',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFFB45309),
                              ),
                            ),
                          ],
                        ),
                      ),
                    const Spacer(),
                    IconButton(
                      icon: Icon(
                        isFavorite ? Icons.favorite : Icons.favorite_border,
                        color: isFavorite ? const Color(0xFFFF6B6B) : Colors.grey,
                      ),
                      onPressed: onFavoriteTap,
                      constraints: const BoxConstraints(),
                      padding: EdgeInsets.zero,
                    ),
                  ],
                ),
                const SizedBox(height: 10),

                // Camp Name
                Text(
                  camp.name,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1A1A2E),
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),

                // Location
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined, size: 15, color: Color(0xFF5A6A7C)),
                    const SizedBox(width: 4),
                    Text(
                      '${camp.city}, ${camp.state} ${camp.zip}',
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF5A6A7C),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Details Grid (Ages, Price, Care Options)
                Wrap(
                  spacing: 12,
                  runSpacing: 6,
                  children: [
                    _buildChip(Icons.child_care, camp.ageMin != null && camp.ageMax != null ? '${camp.ageMin}–${camp.ageMax} yrs' : 'Ages on request'),
                    _buildChip(Icons.category_outlined, camp.type),
                    if (camp.beforeCare == true) _buildChip(Icons.wb_sunny_outlined, 'Early Care'),
                    if (camp.afterCare == true) _buildChip(Icons.nights_stay_outlined, 'Late Care'),
                    if (camp.shuttle == true) _buildChip(Icons.directions_bus_outlined, 'Shuttle'),
                  ],
                ),
                const SizedBox(height: 14),

                const Divider(height: 1),
                const SizedBox(height: 10),

                // Bottom Row: Price & Compare Checkbox
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'WEEKLY PRICE',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF8A9AA8),
                            letterSpacing: 0.5,
                          ),
                        ),
                        Text(
                          camp.price != null ? '\$${camp.price!.toInt()} / wk' : 'Price on request',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFFFF6B6B),
                          ),
                        ),
                      ],
                    ),
                    OutlinedButton.icon(
                      onPressed: onCompareTap,
                      icon: Icon(
                        isSelectedForCompare ? Icons.check_box : Icons.check_box_outline_blank,
                        size: 16,
                        color: isSelectedForCompare ? const Color(0xFFFF6B6B) : const Color(0xFF5A6A7C),
                      ),
                      label: Text(
                        isSelectedForCompare ? 'Comparing' : 'Compare',
                        style: TextStyle(
                          fontSize: 12,
                          color: isSelectedForCompare ? const Color(0xFFFF6B6B) : const Color(0xFF5A6A7C),
                        ),
                      ),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        side: BorderSide(
                          color: isSelectedForCompare ? const Color(0xFFFF6B6B) : Colors.grey.shade300,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: const Color(0xFFF4F6F9),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: const Color(0xFF5A6A7C)),
          const SizedBox(width: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: Color(0xFF5A6A7C),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
