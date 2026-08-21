function [V, chi2, p, gl] = cramersv(a, b)
% Chi-cuadrado de independencia + V de Cramer entre dos variables categoricas.
% La V normaliza el chi2 entre 0 y 1 para poder comparar asociaciones
% (el chi2 solo crece con n y no dice nada del tamano del efecto).

[tabla, chi2, p] = crosstab(a, b);
n = sum(tabla(:));
[r, c] = size(tabla);
gl = (r-1)*(c-1);
V = sqrt(chi2 / (n * min(r-1, c-1)));
end
