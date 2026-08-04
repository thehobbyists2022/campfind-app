import 'package:flutter/material.dart';

class PaywallModal extends StatefulWidget {
  final String featureTrigger;

  const PaywallModal({Key? key, this.featureTrigger = 'Pro Features'}) : super(key: key);

  @override
  State<PaywallModal> createState() => _PaywallModalState();
}

class _PaywallModalState extends State<PaywallModal> {
  int _selectedPlanIndex = 0; // 0 = Yearly ($19.99/yr), 1 = Monthly ($4.99/mo)

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Top Bar Indicator
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),

            // Crown Icon
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF9E6),
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFFFFD700), width: 2),
              ),
              child: const Text('👑', style: TextStyle(fontSize: 36)),
            ),
            const SizedBox(height: 12),

            // Header Title
            const Text(
              'Unlock CampFind Pro',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w800,
                color: Color(0xFF1A1A2E),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Unlock ${widget.featureTrigger} & plan your child\'s summer & winter camps effortlessly.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF5A6A7C),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),

            // Benefits Checklist
            _buildBenefitItem('👨‍👩‍👧‍👦 Multi-Child / Sibling Mode', 'Match camps suitable for 2 children simultaneously'),
            _buildBenefitItem('📅 Session Week 1–8 Picker', 'Align exact weeks across all 1,050 camps'),
            _buildBenefitItem('⚖️ Side-by-Side Comparison', 'Compare price, care hours, and logistics in detail'),
            _buildBenefitItem('🔔 Real-time Availability & Deal Alerts', 'Instant push notifications when spots open up'),
            _buildBenefitItem('📆 One-Tap Calendar Sync', 'Export booked camp weeks directly to Android Calendar'),

            const SizedBox(height: 24),

            // Plan Selection Cards
            // Option 1: Yearly (Best Value)
            GestureDetector(
              onTap: () => setState(() => _selectedPlanIndex = 0),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: _selectedPlanIndex == 0 ? const Color(0xFFFFF9E6) : const Color(0xFFF4F6F9),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _selectedPlanIndex == 0 ? const Color(0xFFFFD700) : Colors.grey.shade300,
                    width: _selectedPlanIndex == 0 ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    Radio<int>(
                      value: 0,
                      groupValue: _selectedPlanIndex,
                      activeColor: const Color(0xFFFF6B6B),
                      onChanged: (val) => setState(() => _selectedPlanIndex = val!),
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                'ANNUAL PASS',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF1A1A2E),
                                ),
                              ),
                              SizedBox(width: 8),
                              Container(
                                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Color(0xFFFF6B6B),
                                  borderRadius: BorderRadius.all(Radius.circular(6)),
                                ),
                                child: Text(
                                  'SAVE 65%',
                                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 2),
                          Text('Instant Access: \$19.99 / year (\$1.66/mo)', style: TextStyle(fontSize: 12, color: Color(0xFF5A6A7C))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),

            // Option 2: Monthly
            GestureDetector(
              onTap: () => setState(() => _selectedPlanIndex = 1),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: _selectedPlanIndex == 1 ? const Color(0xFFFFF9E6) : const Color(0xFFF4F6F9),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _selectedPlanIndex == 1 ? const Color(0xFFFFD700) : Colors.grey.shade300,
                    width: _selectedPlanIndex == 1 ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    Radio<int>(
                      value: 1,
                      groupValue: _selectedPlanIndex,
                      activeColor: const Color(0xFFFF6B6B),
                      onChanged: (val) => setState(() => _selectedPlanIndex = val!),
                    ),
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'MONTHLY ACCESS',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF1A1A2E),
                          ),
                        ),
                        SizedBox(height: 2),
                        Text('\$4.99 / month, cancel anytime', style: TextStyle(fontSize: 12, color: Color(0xFF5A6A7C))),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Unlock Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFF6B6B),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  elevation: 2,
                ),
                onPressed: () {
                  // Trigger In-App Purchase / Free Trial
                  Navigator.pop(context, true);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('🎉 Pro Features Unlocked! Welcome to CampFind Pro.'),
                      backgroundColor: Color(0xFF2E7D32),
                    ),
                  );
                },
                child: Text(
                  _selectedPlanIndex == 0 ? 'Unlock Pro Annual Pass (\$19.99)' : 'Unlock Pro Monthly Pass (\$4.99)',
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                ),
              ),
            ),

            const SizedBox(height: 12),
            const Text(
              'Recurring billing. Cancel anytime in Google Play Store settings.',
              style: TextStyle(fontSize: 11, color: Color(0xFF8A9AA8)),
            ),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }

  Widget _buildBenefitItem(String title, String subtitle) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          const Icon(Icons.check_circle_rounded, color: Color(0xFF2E7D32), size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF1A1A2E))),
                Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF5A6A7C))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
