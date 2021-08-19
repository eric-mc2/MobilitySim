# IGM Equations

Writing out the IGM equations so I can understand why this model blows up.

$$ \begin{equation}
Y_{i,t+1} = \alpha + \beta X_i Y_{i,t} + \epsilon 
\end{equation} $$

$$ \begin{equation}
Y_{i,t+1} = \alpha + \phi H_{i,t} \xi_{i,t} + \epsilon
\end{equation} $$

$$ \begin{equation}
T_{n,t} = \tau \sum Y_{i \in n,t}
\end{equation} $$

$$ \begin{equation}
D_{n,t} = T_{n,t} / \nu(p_{n,t})
\end{equation} $$

$$ \begin{equation}
\nu(p_{n,t}) \approx \lambda p_{n,t}
\end{equation} $$

$$ \begin{equation}
H_{i,t} = \theta(s)D_{n,t}
\end{equation} $$

$$ \begin{equation}
s_{i,t} = \zeta(Y_i, \bar Y_{-i}) = \zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1))
\end{equation} $$

Back substitution:

$$ \begin{aligned}
H_{i,t} &= \theta(\zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1)))D_{n,t} \\
&= \theta(\zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1)))T_{n,t} / \nu(p_{n,t}) \\
&= \theta(\zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1)))T_{n,t} / (\lambda p_{n,t}) \\
&= \theta(\zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1)))(\tau \sum Y_{i \in n,t}) / (\lambda p_{n,t}) \\
&= \theta(\zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1)))(\tau p_{n,t} \bar Y_n) / (\lambda p_{n,t}) \\
&= \theta(\zeta(Y_i, (\sum Y - Y_i)/(p_{n,t}-1)))(\tau \bar Y_n) / \lambda \\
&\approx \theta(\zeta(Y_i, \bar Y_n))(\tau \bar Y_n) / \lambda \\
\end{aligned} $$

$$ \begin{aligned}
Y_{i,t+1} &= \alpha + \phi H_{i,t} \xi_{i,t} + \epsilon \\
Y_{i,t+1} &\approx \alpha + \phi \tau \xi_{i,t} \bar Y_n \theta(\zeta(Y_i, \bar Y_n)) / \lambda  + \epsilon \\
\end{aligned}$$

Require:
* $\theta(s) \ge 0$
* $d\theta(s)/ds \ge 0 $
* $\partial \zeta(Y,\bar Y)/ \partial Y \ge 0 $
* $\partial \zeta(Y,\bar Y)/ \partial \bar Y \ge 0 $
* $\partial^2 \zeta(Y, \bar Y) / \partial Y \partial \bar Y \ge 0 $

Let $\theta(s) := \beta s$

Let $\zeta(Y, \bar Y) = log(Y) log(\bar Y) $

Then $\partial \zeta(\cdot) / \partial Y = log(\bar Y)/Y $

Then $\partial^2 \zeta(\cdot) / \partial Y \partial \bar Y = 1/(Y\bar Y) $

---

Let $\zeta(Y, \bar Y) = Y^\gamma \bar Y^{1-\gamma}$

Then $\partial \zeta(\cdot) / \partial Y = \gamma Y^{\gamma-1}\bar Y^{1-\gamma}$

Then $\partial^2 \zeta(\cdot) / \partial Y \partial \bar Y = \gamma Y^{\gamma-1}(1-\gamma)\bar Y^{-\gamma} = \gamma (1-\gamma)Y^{\gamma-1}\bar Y^{-\gamma} $

---

Let $\zeta(Y, \bar Y) = (Y + \bar Y)^\gamma $

Then $\partial \zeta(\cdot) / \partial Y = \gamma (Y + \bar Y)^{\gamma - 1} $

Then $\partial^2 \zeta(\cdot) / \partial Y \partial \bar Y = \gamma (\gamma-1) (Y + \bar Y)^{\gamma - 2} $

