//
// Generated by JTB 1.1.2
//

package jde.parser.syntaxtree;

/**
 * Grammar production:
 * <PRE>
 * f0 -> ( "~" | "!" ) UnaryExpression()
 *       | CastExpression()
 *       | PostfixExpression()
 * </PRE>
 */
public class UnaryExpressionNotPlusMinus implements Node {
   public NodeChoice f0;

   public UnaryExpressionNotPlusMinus(NodeChoice n0) {
      f0 = n0;
   }

   public void accept(jde.parser.visitor.Visitor v) {
      v.visit(this);
   }
}
