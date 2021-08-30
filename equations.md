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

--- 
Assume just one neighborhood. Let $\alpha , \epsilon := 0 $. Let $\xi := 1 $

$$ \begin{aligned}
Y_{i,t+1} &\approx \frac{\phi \tau }{\lambda} \theta(\zeta(Y_{i,t}, \bar Y_{t}))  \bar Y_{t}\\
&\approx \frac{\phi \tau }{\lambda}\theta(\zeta(Y_{i,t}, \bar Y_{t}))\frac{\sum {Y_{i,t}}}{n}   \\
&\approx \frac{\phi \tau }{\lambda}\theta(\zeta(Y_{i,t}, \bar Y_{t})) \frac{\sum {\frac{\phi \tau }{\lambda}\theta(\zeta(Y_{i,t-1}, \bar Y_{t-1}))\bar Y_{t-1} }}{n}  \\
&\approx \left(\frac{\phi \tau }{\lambda}\right)^2 \theta(\zeta(Y_{i,t}, \bar Y_{t})) \frac{\sum {\theta(\zeta(Y_{i,t-1}, \bar Y_{t-1})) }}{n} \bar Y_{t-1} \\
&\approx \left(\frac{\phi \tau }{\lambda}\right)^2 \theta(\zeta(Y_{i,t}, \bar Y_{t})) \frac{\sum {\theta(\zeta(Y_{i,t-1}, \bar Y_{t-1})) }}{n} \frac{\sum{Y_{i,t-1}}}{n} \\
&\approx \left(\frac{\phi \tau }{\lambda}\right)^2 \theta(\zeta(Y_{i,t}, \bar Y_{t})) \frac{\sum {\theta(\zeta(Y_{i,t-1}, \bar Y_{t-1})) }}{n} 
\frac{\sum {\frac{\phi \tau }{\lambda}\theta(\zeta(Y_{i,t-2}, \bar Y_{t-2}))\bar Y_{t-2} }}{n}  \\
&\approx \left(\frac{\phi \tau }{\lambda}\right)^3 \theta(\zeta(Y_{i,t}, \bar Y_{t})) \frac{\sum {\theta(\zeta(Y_{i,t-1}, \bar Y_{t-1})) }}{n} 
\frac{\sum {\theta(\zeta(Y_{i,t-2}, \bar Y_{t-2})) }}{n} \bar Y_{t-2} \\
&... \\
Y_{i,t} &\approx \left(\frac{\phi \tau }{\lambda}\right)^t  \bar Y_{0}  \theta(\zeta(Y_{i,t-1}, \bar Y_{t-1}))\prod_{s=0}^{s=t-2} {\bar \theta_s} \\
\end{aligned}$$

So this will blow up in two cases. For a stable system we require:
$$\begin{aligned} 
    0 \leq \phi \tau / \lambda \leq 1 \\
    \implies \phi \tau \leq \nu(p_{n,t}) / p_{n,t} \\
    \implies \text{income return on human capital} \\
    \leq \text{edu. economy of scale} / \text{tax rate}
\end{aligned}$$
which means you either need some surplus in human capital that doesn't translate to income, or you need to not utilize a lot of the income in education (low taxes), even if you have a high return on education to income.

We also require $\bar \theta > 1$. This is a harder limitation to meet. We could stuff $\theta(s) := \sigma(s)$ to meet the bound. But generally, economists probably wouldn't want to put a hard cap on human capital this way,
because it necessarily caps $\bar Y$ and economists can't stomach a world with a finite capacity for growth.

The original problem is that $H := \theta D$. So we should check if a multiplicative process is necessary for dynastic growth/diffusion. If not,
try an additive process or something. If so, we need to find a way to limit 
$\theta$, maybe by limiting $\zeta$ or something.