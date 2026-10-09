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

    try {
      final client = HttpClient();
      final request = await client.postUrl(Uri.parse('https://formsubmit.co/ajax/wingsoar2023@gmail.com'));
      request.headers.set('content-type', 'application/json');
      request.headers.set('accept', 'application/json');
      final payload = jsonEncode({
        '_subject': '🏕️ CampFind Director Verification: ${_campNameController.text.trim()}',
        'Request_Type': 'Free Director Listing Claim & Verification',
        'Camp_Name': _campNameController.text.trim(),
        'Director_Name': _directorNameController.text.trim(),
        'Email': _emailController.text.trim(),
        'Phone_Website': _phoneController.text.trim(),
        'Notes_Updates': _notesController.text.trim(),
        'Submitted_From': 'CampFind Mobile App',
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
        title: const Text('Verification Request Received'),
        content: Text(
          'Thank you for submitting your verification details for ${_campNameController.text.trim()}.\n\nOur directory team will verify your credentials and update your listing within 24 hours.',
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
          'Camp Director Verification',
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
                            'Verify & Update Your Camp Listing',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF166534),
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Are you the official director or administrator? Submit your credentials to verify your camp listing and request updates to session dates, tuition, and enrollment links for free.',
                            style: TextStyle(fontSize: 12, color: Color(0xFF15803D), height: 1.3),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
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
                'Director / Administrator Name *',
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
                'Official Phone & Website',
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
                'Listing Corrections & Session Updates',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _notesController,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: 'Describe session dates, age brackets, weekly tuition, or registration website link...',
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
                          'Submit Verification Request →',
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
}
