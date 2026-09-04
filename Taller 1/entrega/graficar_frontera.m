function graficar_frontera(X, d, w, b, umbral, titulo)
% GRAFICAR_FRONTERA  Dibuja los patrones de una compuerta de 2 entradas y la
% recta que separa las dos clases: w1*x1 + w2*x2 + b = umbral.
hold on
clases = unique(d);
scatter(X(d == clases(1), 1), X(d == clases(1), 2), 80, 'r', 'filled');
scatter(X(d == clases(2), 1), X(d == clases(2), 2), 80, 'b', 'filled');
x1 = linspace(-0.5, 1.5, 100);
if abs(w(2)) > 1e-9
    x2 = (umbral - b - w(1) * x1) / w(2);
    plot(x1, x2, 'k-', 'LineWidth', 1.5);
else
    xline((umbral - b) / w(1), 'k-', 'LineWidth', 1.5);
end
xlim([-0.5 1.5]); ylim([-0.5 1.5]); grid on
xlabel('x_1'); ylabel('x_2');
legend('salida min', 'salida max', 'frontera', 'Location', 'best');
title(titulo);
hold off
end
