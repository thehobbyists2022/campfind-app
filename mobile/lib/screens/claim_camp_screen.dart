import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';

class ClaimCampScreen extends StatefulWidget {
  final String initialCampName;
  final String initialCampId;

  const ClaimCampScreen({
    super.key,
    this.initialCampName = '',
    this.initialCampId = '',
  });

  @override
  State<ClaimCampScreen> createState() => _ClaimCampScreenState();
}

class _ClaimCampScreenState extends State<ClaimCampScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _campNameController;
  final TextEditingController _directorNameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  String _partnerTier = 'featured'; // 'featured', 'verified', 'free'
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _campNameController = TextEditingController(text: widget.initialCampName);
  }

  @override
  void dispose() {
    _campNameController.dispose();
    _directorNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSubmitting = true;
    });

    final tierTitles = {
      'featured': '⭐ Featured Regional Sponsor (\$299/Quarter)',
      'verified': '🛡️ Verified Partner Badge (\$99/Year)',
      'free': '✅ Free Listing Claim (\$0)',
    };

    try {
      final client = HttpClient();
      final request = await client.postUrl(Uri.parse('https://formsubmit.co/ajax/wingsoar2023@gmail.com'));
      request.headers.set('content-type', 'application/json');
      request.headers.set('accept', 'application/json');
      final payload = jsonEncode({
        '_subject': '🏕️ CampFind Partner Application: [${tierTitles[_partnerTier]}] ${_campNameController.text.trim()}',
        'Selected_Tier': tierTitles[_partnerTier],
        'Camp_Name': _campNameController.text.trim(),
        'Director_Name': _directorNameController.text.trim(),
        'Email': _emailController.text.trim(),
        'Phone_Website': _phoneController.text.trim(),
        'Notes': _notesController.text.trim(),
        'Submitted_From': 'CampFind App (iOS & Android)',
        'Submitted_At': DateTime.now().toIso8601String(),
      });
      request.add(utf8.encode(payload));
      await request.close();
      client.close();
    } catch (e) {
      debugPrint('Claim submission error: $e');
    }

    if (!mounted) return;

    setState(() {
      _isSubmitting = false;
    });

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        icon: const Icon(Icons.check_circle, color: Color(0xFF16A34A), size: 48),
        title: const Text('Partner Application Received'),
        content: Text(
          'Thank you for submitting your partnership application for ${_campNameController.text.trim()}.\n\nOur CampFind partner team will review your credentials and send onboarding & verification details to ${_emailController.text.trim()} within 24 hours.',
          style: const TextStyle(fontSize: 14, height: 1.4),
        ),
        actions: [
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: const Color(0xFF16A34A)),
            onPressed: () {
              Navigator.pop(ctx);
              Navigator.pop(context);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        title: const Text(
          'Camp Director Partner Portal',
          style: TextStyle(
            color: Color(0xFF1A1A2E),
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF1A1A2E)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFF0FDF4), Color(0xFFDCFCE7)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: const Row(
                  children: [
                    Text('🏕️', style: TextStyle(fontSize: 34)),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Reach Thousands of Local Families',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF166534),
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'CampFind helps parents discover summer & winter camps. Claim your listing, boost your visibility, or become a featured sponsor.',
                            style: TextStyle(fontSize: 12, color: Color(0xFF15803D), height: 1.3),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Partnership Tier Selection
              const Text(
                'Select Partnership Tier *',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 10),

              // Tier 1: Featured Sponsor ($299/Quarter)
              _buildTierCard(
                tierId: 'featured',
                badgeText: 'MOST POPULAR · TOP ROI',
                badgeColor: const Color(0xFFEA580C),
                title: 'Featured Regional Sponsor',
                price: '\$299 / quarter',
                description: 'Ranked at the top of search results in your city/category, official gold badge, direct enrollment link, and instant OTA live updates.',
                icon: Icons.workspace_premium,
                accentColor: const Color(0xFFF59E0B),
              ),
              const SizedBox(height: 10),

              // Tier 2: Verified Partner ($99/Year)
              _buildTierCard(
                tierId: 'verified',
                badgeText: 'RECOMMENDED',
                badgeColor: const Color(0xFF2563EB),
                title: 'Verified Partner Badge',
                price: '\$99 / year',
                description: 'Official blue Verified badge on your camp card, direct website & call links enabled, and 24-hr priority updates.',
                icon: Icons.verified_user,
                accentColor: const Color(0xFF3B82F6),
              ),
              const SizedBox(height: 10),

              // Tier 3: Free Listing Claim ($0)
              _buildTierCard(
                tierId: 'free',
                badgeText: 'BASIC',
                badgeColor: const Color(0xFF64748B),
                title: 'Free Listing Claim',
                price: 'Free',
                description: 'Verify identity as camp director and suggest corrections to contact info and address.',
                icon: Icons.check_circle_outline,
                accentColor: const Color(0xFF64748B),
              ),

              const SizedBox(height: 24),

              // Camp Name
              const Text(
                'Camp Name *',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _campNameController,
                validator: (val) => val == null || val.trim().isEmpty ? 'Please enter camp name' : null,
                decoration: InputDecoration(
                  hintText: 'e.g. Carlsbad STEM Adventure Camp',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 18),

              // Director Name
              const Text(
                'Director / Contact Name *',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _directorNameController,
                validator: (val) => val == null || val.trim().isEmpty ? 'Please enter your name' : null,
                decoration: InputDecoration(
                  hintText: 'e.g. Dr. Jane Smith, Executive Director',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 18),

              // Work Email
              const Text(
                'Official Work Email *',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                validator: (val) => val == null || !val.contains('@') ? 'Please enter a valid work email' : null,
                decoration: InputDecoration(
                  hintText: 'director@campdomain.org',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 18),

              // Phone / Website
              const Text(
                'Phone & Official Website',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _phoneController,
                decoration: InputDecoration(
                  hintText: '(858) 555-0199 | https://mycamp.org',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 18),

              // Notes / Updates
              const Text(
                'Notes & Enrollment Details',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _notesController,
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'Mention open sessions, early-bird promo discounts, or registration URLs...',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 28),

              // Submit Button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF16A34A),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    elevation: 2,
                  ),
                  onPressed: _isSubmitting ? null : _handleSubmit,
                  child: _isSubmitting
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
                        )
                      : const Text(
                          'Submit Partnership Application →',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTierCard({
    required String tierId,
    required String badgeText,
    required Color badgeColor,
    required String title,
    required String price,
    required String description,
    required IconData icon,
    required Color accentColor,
  }) {
    final isSelected = _partnerTier == tierId;

    return GestureDetector(
      onTap: () => setState(() => _partnerTier = tierId),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected ? accentColor.withValues(alpha: 0.08) : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isSelected ? accentColor : const Color(0xFFE2E8F0),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ignore: deprecated_member_use
            Radio<String>(
              value: tierId,
              // ignore: deprecated_member_use
              groupValue: _partnerTier,
              activeColor: accentColor,
              // ignore: deprecated_member_use
              onChanged: (val) => setState(() => _partnerTier = val ?? 'featured'),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: badgeColor,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          badgeText,
                          style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                        ),
                      ),
                      const Spacer(),
                      Text(
                        price,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? accentColor : const Color(0xFF1E293B),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Icon(icon, size: 16, color: accentColor),
                      const SizedBox(width: 6),
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
