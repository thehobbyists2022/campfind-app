import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/subscription_service.dart';

class PaywallModal extends StatefulWidget {
  final String featureTrigger;

  const PaywallModal({
    super.key,
    this.featureTrigger = 'Pro Features',
  });

  static Future<bool?> show(BuildContext context, {String featureTrigger = 'Pro Features'}) {
    return showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => PaywallModal(featureTrigger: featureTrigger),
    );
  }

  @override
  State<PaywallModal> createState() => _PaywallModalState();
}

class _PaywallModalState extends State<PaywallModal> {
  int _selectedPlanIndex = 0; // 0 = Yearly ($19.99/yr), 1 = Monthly ($4.99/mo)
  bool _isLoading = false;

  void _handleUnlock() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(milliseconds: 600)); // Smooth UX transition

    final tier = _selectedPlanIndex == 0 ? 'yearly' : 'monthly';
    final days = _selectedPlanIndex == 0 ? 365 : 30;
    await SubscriptionService().activateSubscription(tier: tier, days: days);

    if (mounted) {
      setState(() => _isLoading = false);
      Navigator.pop(context, true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('🎉 Welcome to CampFind Pro! All features unlocked.'),
          backgroundColor: Color(0xFF16A34A),
          duration: Duration(seconds: 3),
        ),
      );
    }
  }

  void _showPromoCodeDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Redeem Promo / VIP Code', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Enter your partner or early supporter code to unlock CampFind Pro:', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(
                hintText: 'e.g. CAMPFINDVIP',
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: const Color(0xFFFF6B6B)),
            onPressed: () async {
              final code = controller.text.trim();
              final success = await SubscriptionService().redeemPromoCode(code);
              if (ctx.mounted) Navigator.pop(ctx);
              if (!mounted) return;

              if (success) {
                Navigator.pop(context, true);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('🎉 Promo Code "$code" successfully activated!'),
                    backgroundColor: const Color(0xFF16A34A),
                  ),
                );
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Invalid code. Please check and try again.'),
                    backgroundColor: Color(0xFFDC2626),
                  ),
                );
              }
            },
            child: const Text('Redeem'),
          ),
        ],
      ),
    );
  }

  void _handleRestore() async {
    setState(() => _isLoading = true);
    final restored = await SubscriptionService().restorePurchases();
    setState(() => _isLoading = false);

    if (mounted) {
      if (restored) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Purchase restored successfully!'),
            backgroundColor: Color(0xFF16A34A),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No active subscription found to restore.'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Handle bar
            Container(
              width: 44,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),

            // Crown Header
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF3C7),
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFFF59E0B), width: 1.5),
              ),
              child: const Icon(Icons.workspace_premium, color: Color(0xFFD97706), size: 36),
            ),
            const SizedBox(height: 12),

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
              'Unlock ${widget.featureTrigger} & plan your children\'s summer effortlessly.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF5A6A7C),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),

            // Benefit List
            _buildBenefitItem('⚖️ Unlimited Camp Comparison', 'Compare up to 5 camps side-by-side with full details'),
            _buildBenefitItem('👨‍👩‍👧‍👦 Multi-Child / Sibling Planner', 'Align overlapping weeks & locations for multiple kids'),
            _buildBenefitItem('📅 Session Week 1–8 Alignment', 'Match exact weekly schedules across 5,000+ camps'),
            _buildBenefitItem('📆 1-Tap Calendar Export', 'Sync booked sessions straight to Apple & Google Calendar'),
            _buildBenefitItem('🔔 Early-Bird & Discount Radar', 'Spot open slots and early discounts before camps fill up'),

            const SizedBox(height: 22),

            // Plan Options
            // Option 0: Yearly (Best Value)
            GestureDetector(
              onTap: () => setState(() => _selectedPlanIndex = 0),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: _selectedPlanIndex == 0 ? const Color(0xFFFFFBEB) : const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _selectedPlanIndex == 0 ? const Color(0xFFF59E0B) : const Color(0xFFE2E8F0),
                    width: _selectedPlanIndex == 0 ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    // ignore: deprecated_member_use
                    Radio<int>(
                      value: 0,
                      // ignore: deprecated_member_use
                      groupValue: _selectedPlanIndex,
                      activeColor: const Color(0xFFD97706),
                      // ignore: deprecated_member_use
                      onChanged: (val) => setState(() => _selectedPlanIndex = val ?? 0),
                    ),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                'Yearly Pass',
                                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E293B)),
                              ),
                              SizedBox(width: 8),
                              DecoratedBox(
                                decoration: BoxDecoration(
                                  color: Color(0xFF16A34A),
                                  borderRadius: BorderRadius.all(Radius.circular(6)),
                                ),
                                child: Padding(
                                  padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  child: Text('SAVE 66%', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                                ),
                              ),
                            ],
                          ),
                          Text('\$1.66 / month (Billed \$19.99 / year)', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                        ],
                      ),
                    ),
                    const Text(
                      '\$19.99/yr',
                      style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: Color(0xFF1E293B)),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),

            // Option 1: Monthly
            GestureDetector(
              onTap: () => setState(() => _selectedPlanIndex = 1),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: _selectedPlanIndex == 1 ? const Color(0xFFFFFBEB) : const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _selectedPlanIndex == 1 ? const Color(0xFFF59E0B) : const Color(0xFFE2E8F0),
                    width: _selectedPlanIndex == 1 ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    // ignore: deprecated_member_use
                    Radio<int>(
                      value: 1,
                      // ignore: deprecated_member_use
                      groupValue: _selectedPlanIndex,
                      activeColor: const Color(0xFFD97706),
                      // ignore: deprecated_member_use
                      onChanged: (val) => setState(() => _selectedPlanIndex = val ?? 1),
                    ),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Monthly Pass',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E293B)),
                          ),
                          Text('Billed monthly, cancel anytime', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                        ],
                      ),
                    ),
                    const Text(
                      '\$4.99/mo',
                      style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: Color(0xFF1E293B)),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Action Button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFFFF6B6B),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  elevation: 2,
                ),
                onPressed: _isLoading ? null : _handleUnlock,
                child: _isLoading
                    ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                    : Text(
                        _selectedPlanIndex == 0 ? 'Start Yearly Pass — \$19.99' : 'Start Monthly Pass — \$4.99',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
            ),

            const SizedBox(height: 14),

            // Auxiliary Links (Redeem Promo Code & Restore)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextButton(
                  onPressed: _showPromoCodeDialog,
                  child: const Text('Redeem Promo Code', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                ),
                const Text('•', style: TextStyle(color: Color(0xFFCBD5E1))),
                TextButton(
                  onPressed: _handleRestore,
                  child: const Text('Restore Purchases', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                ),
              ],
            ),

            // Legal Footnote
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                InkWell(
                  onTap: () => launchUrl(Uri.parse('https://campfind-app.netlify.app/privacy.html'), mode: LaunchMode.externalApplication),
                  child: const Text('Privacy Policy', style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8), decoration: TextDecoration.underline)),
                ),
                const Text('  |  ', style: TextStyle(fontSize: 10, color: Color(0xFFCBD5E1))),
                InkWell(
                  onTap: () => launchUrl(Uri.parse('https://campfind-app.netlify.app/privacy.html'), mode: LaunchMode.externalApplication),
                  child: const Text('Terms of Use', style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8), decoration: TextDecoration.underline)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBenefitItem(String title, String subtitle) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF1E293B)),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
