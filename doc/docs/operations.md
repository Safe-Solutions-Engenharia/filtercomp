# Flash Operations

$$
\text{Burn Rate} \left(\frac {kg} {m²s}\right) = 1.27 \cdot 10^{\text{-6}} \rho_f  
\left[ 
  \frac{\Delta H_{\text{c}}}
       {\Delta H_{\text{v}} + c_p (T_{\text{b}} - T_{\text{f}})}
\right]
$$

Where:

- \( \rho_f \) = **Density** of the fuel \((\text{kg/m}^3)\)
- \( \Delta H_{\text{c}} \) = **Heat of combustion** \((\text{kJ/kg})\)
- \( \Delta H_{\text{v}} \) = **Heat of vaporization** \((\text{kJ/kg})\)
- \( c_p \) = **Specific heat** \((\text{kJ/kg·K})\)
- \( T_{\text{b}} \) = **Boiling point temperature** of the fuel \((\text{K})\)
- \( T_{\text{f}} \) = **Actual fuel temperature** \((\text{K})\)

$$
\text{Evaporation Rate} \left(\frac {kg} {m²s}\right) = k \cdot \left( \frac{T_{\text{b}} - T_{\text{f}}}{\Delta H_{\text{v}}} \right)
$$

Where:

- \( k \) = **Constant** (for average soil and concrete; k = 10.5)
- \( T_{\text{b}} \) = **Boiling point temperature** of the fuel \((\text{K})\)
- \( T_{\text{f}} \) = **Actual fuel temperature** \((\text{K})\)
- \( \Delta H_{\text{v}} \) = **Heat of vaporization** \((\text{kJ/kg})\)


```mermaid
  flowchart TD
    A[Start] --> B[Save state & 
    set vapor_fraction = 0];
    B --> C[Loop: vapor_fraction < 1];
    C --> D[Try flash calculation at 
    T = release + ΔT];
    D --> E{Flash succeeds?};
    E -->|Yes| F{vapor_fraction < 1?};
    F -->|Yes| G[Increase ΔT by 50 K] --> C;
    F -->|No| H[Go to refinement loop];
    E -->|No| I[Adjust tolerances 
    and retries] --> D;
```
*Representative fluxogram of the buble temperature*

```mermaid
  flowchart TD
    A[Refinement loop] --> B[Loop: vapor_fraction >= 1];
    B --> C[Decrease ΔT by 1 K];
    C --> D[Try flash calculation];
    D --> E{Flash succeeds?};
    E -->|Yes| F{vapor_fraction < 1?};
    E -->|No| G[Adjust tolerances 
    and retries] --> D;
    F --> |No| B[Loop: vapor_fraction >= 1];
    F --> |Yes| H[Refined temperature found];
    H --> I[Return ΔT];
```
*Representative fluxogram of the buble temperature*
