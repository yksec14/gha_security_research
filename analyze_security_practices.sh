
echo "START: E2 - Analyze security practices"
echo "  Start date: $1"
echo "  End date:   $2"

echo ""
echo "  Analyzing Practice 1: CODEOWNERS"
python src/analyze_security_practices/analyze_p1_codeowners.py --start $1 --end $2

echo ""
echo "  Analyzing Practice 2: Mitigating Script Injection"
python src/analyze_security_practices/analyze_p2_mitigating_injection.py --start $1 --end $2

echo ""
echo "  Analyzing Practice 3: OpenSSf Scorecard"
python src/analyze_security_practices/analyze_p3_scorecard.py --start $1 --end $2

echo ""
echo "  Analyzing Practice 4: Pinning Third-Party Actions"
python src/analyze_security_practices/analyze_p4_pinning_actions.py --start $1 --end $2

echo ""
echo "  Analyzing Practice 5: Dependabot"
python src/analyze_security_practices/analyze_p5_dependabot.py --start $1 --end $2

echo ""
python src/analyze_security_practices/get_result.py --start $1 --end $2
python src/analyze_security_practices/show_result.py --start $1 --end $2

echo "FINISH: E2 - Analyze security practices"
