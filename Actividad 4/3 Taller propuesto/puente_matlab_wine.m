% Lee los CSV que exporta el cuaderno (TODO 6) y agrupa los vinos con fcm.
% Se ejecuta en la misma carpeta del cuaderno, después de haberlo ejecutado.
tr = readmatrix("wine_4car_train.csv");
te = readmatrix("wine_4car_test.csv");
datos = [tr; te];
X = normalize(datos(:, 1:4), "range");        % misma escala [0, 1] que en Python
clase = datos(:, 5);
grupoPython = readmatrix("wine_fcm_python.csv");

opciones = fcmOptions(NumClusters=3, Exponent=2, MaxNumIteration=300, MinImprovement=1e-6, Verbose=false);
[centros, U] = fcm(X, opciones);
[~, grupo] = max(U, [], 1);
grupo = grupo(:);
fpc = sum(U .^ 2, "all") / size(U, 2);

fprintf("Vinos: %d | coeficiente de partición: %.3f\n", size(X, 1), fpc);
fprintf("ARI frente a los cultivares: %.3f\n", ari(grupo, clase));
fprintf("ARI frente a los grupos del FCM de Python: %.3f\n", ari(grupo, grupoPython));
disp("Centros ordenados por la primera característica:");
disp(round(sortrows(centros, 1), 4));
disp("Grupo frente a cultivar:");
disp(crosstab(grupo, clase));
writematrix(grupo, "fcm_matlab_grupos.csv");

function r = ari(a, b)
    % Índice de Rand ajustado entre dos particiones
    t = crosstab(a, b);
    n = sum(t, "all");
    sumaPares = sum(t .* (t - 1) / 2, "all");
    filas = sum(sum(t, 2) .* (sum(t, 2) - 1) / 2);
    columnas = sum(sum(t, 1) .* (sum(t, 1) - 1) / 2);
    esperado = filas * columnas / (n * (n - 1) / 2);
    r = (sumaPares - esperado) / ((filas + columnas) / 2 - esperado);
end
