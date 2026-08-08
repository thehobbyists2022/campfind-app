import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/camp_model.dart';

class CampDetailScreen extends StatelessWidget {
  final Camp camp;
  final bool isFavorite;
  final VoidCallback onFavoriteTap;

  const CampDetailScreen({
    super.key,
    required this.camp,
    required this.isFavorite,
    required this.onFavoriteTap,
  });

  Future<void> _launchUrl(BuildContext context, String urlString) async {
    String cleanUrl = urlString.trim();
    if (cleanUrl.isEmpty) {
      final query = Uri.encodeComponent('${camp.name} ${camp.city} ${camp.state} camp website');
      cleanUrl = 'https://www.google.com/search?q=$query';
    } else if (cleanUrl.startsWith('http://')) {
      cleanUrl = 'https://${cleanUrl.substring(7)}';
    } else if (!cleanUrl.startsWith('https://')) {
      cleanUrl = 'https://$cleanUrl';
    }

    final Uri? url = Uri.tryParse(cleanUrl);
    if (url == null || !url.hasScheme || url.host.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('This website link is unavailable.')),
      );
      return;
    }
    final opened = await launchUrl(url, mode: LaunchMode.externalApplication);
    if (!opened && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to open the website on this device.')),
      );
    }
  }

  Future<void> _makeCall(String phoneNumber) async {
    if (phoneNumber.isEmpty) return;
    final Uri url = Uri.parse('tel:$phoneNumber');
    if (await canLaunchUrl(url)) {
      await launchUrl(url);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF1A1A2E)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          camp.name,
          style: const TextStyle(
            color: Color(0xFF1A1A2E),
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(
              isFavorite ? Icons.favorite : Icons.favorite_border,
              color: isFavorite ? const Color(0xFFFF6B6B) : Colors.grey,
            ),
            onPressed: onFavoriteTap,
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Banner Card
            Container(
              width: double.infinity,
              color: Colors.white,
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF4ECDC4).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          camp.theme.toUpperCase(),
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF3AB5AD),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      if (camp.provider.toLowerCase() == 'city')
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFCCFBF1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            '🏛️ City-Run',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF0D9488),
                            ),
                          ),
                        ),
                      if (camp.acaVerified)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFE8F5E9),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            '✓ ACA Accredited',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF2E7D32),
                            ),
                          ),
                        )
                      else if (camp.unverified)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEF3C7),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            'Unverified',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFFB45309),
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    camp.name,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF1A1A2E),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(Icons.location_on, size: 18, color: Color(0xFFFF6B6B)),
                      const SizedBox(width: 4),
                      Text(
                        '${camp.city}, ${camp.state}${camp.zip.isNotEmpty ? ' ${camp.zip}' : ''}',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Color(0xFF5A6A7C),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Quick Stats Row
            Container(
              color: Colors.white,
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatItem('WEEKLY PRICE', camp.price != null ? '\$${camp.price!.toInt()}' : 'On request', const Color(0xFFFF6B6B)),
                  _buildStatItem('AGES', camp.ageMin != null && camp.ageMax != null ? '${camp.ageMin}–${camp.ageMax} yrs' : 'On request', const Color(0xFF2C3E50)),
                  _buildStatItem('TYPE', camp.type, const Color(0xFF4ECDC4)),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Action Buttons (Call, Website, Email)
            Container(
              color: Colors.white,
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  if (camp.website.isNotEmpty)
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _launchUrl(context, camp.website),
                        icon: const Icon(Icons.language, size: 16),
                        label: const Text('Website'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFFF6B6B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                    ),
                  if (camp.website.isNotEmpty && camp.phone.isNotEmpty) const SizedBox(width: 10),
                  if (camp.phone.isNotEmpty)
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _makeCall(camp.phone),
                        icon: const Icon(Icons.phone, size: 16),
                        label: const Text('Call'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF2C3E50),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Description Section
            Container(
              width: double.infinity,
              color: Colors.white,
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'About This Camp',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1A1A2E),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    camp.description.isNotEmpty ? camp.description : 'Contact the camp directly for program details.',
                    style: const TextStyle(
                      fontSize: 14,
                      color: Color(0xFF5A6A7C),
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Extended Care & Logistics Specs
            Container(
              width: double.infinity,
              color: Colors.white,
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Extended Care & Logistics',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1A1A2E),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildLogisticsRow(Icons.wb_sunny_outlined, 'Early Care (Before 8 AM)', camp.beforeCare),
                  _buildLogisticsRow(Icons.nights_stay_outlined, 'Late Care (After 5 PM)', camp.afterCare),
                  _buildLogisticsRow(Icons.directions_bus_outlined, 'Shuttle Bus Service', camp.shuttle),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Session Weeks Timeline
            Container(
              width: double.infinity,
              color: Colors.white,
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Session Weeks Timeline',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1A1A2E),
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (camp.weeks.isEmpty)
                    const Text(
                      'Session schedule not published. Please contact the camp or check its official website.',
                      style: TextStyle(
                        fontSize: 14,
                        color: Color(0xFF5A6A7C),
                        height: 1.5,
                      ),
                    )
                  else
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: List.generate(8, (index) {
                      final weekNum = index + 1;
                      final isAvailable = camp.weeks.contains(weekNum);
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: isAvailable ? const Color(0xFF4ECDC4).withValues(alpha: 0.15) : const Color(0xFFF4F6F9),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: isAvailable ? const Color(0xFF4ECDC4) : Colors.grey.shade300,
                          ),
                        ),
                        child: Text(
                          'Week $weekNum ${isAvailable ? "✓" : "—"}',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: isAvailable ? FontWeight.bold : FontWeight.normal,
                            color: isAvailable ? const Color(0xFF3AB5AD) : Colors.grey,
                          ),
                        ),
                      );
                      }),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String title, String value, Color valueColor) {
    return Column(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: Color(0xFF8A9AA8),
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: valueColor,
          ),
        ),
      ],
    );
  }

  Widget _buildLogisticsRow(IconData icon, String label, bool? isAvailable) {
    final bool? status = isAvailable;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 18, color: status == true ? const Color(0xFF2E7D32) : Colors.grey),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: status == true ? const Color(0xFF1A1A2E) : Colors.grey,
                fontWeight: status == true ? FontWeight.w500 : FontWeight.normal,
              ),
            ),
          ),
          Icon(
            status == true ? Icons.check_circle : Icons.cancel_outlined,
            size: 18,
            color: status == true ? const Color(0xFF2E7D32) : Colors.grey.shade400,
          ),
        ],
      ),
    );
  }
}
