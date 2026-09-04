%% Taller 1, puntos 1 a 3: perceptron simple y compuertas
clear; close all; clc

%% Parametros del modelo
regla      = 3;        % 1: d*x   2: (d-y)*x   3: alpha*(d-y)*x
alpha      = 0.1;
umbral     = 0;
salida     = [-1 1];
max_epocas = 100;
semilla    = 1;

%% AND de 2 entradas
[X, d] = compuerta('AND', 2, salida);
[w, b, epocas, convergio] = perceptron(X, d, regla, alpha, umbral, salida, max_epocas, semilla);
epocas, convergio
table(X(:,1), X(:,2), d, predecir(X, w, b, umbral, salida), 'VariableNames', {'x1','x2','deseada','modelo'})

figure
subplot(1,2,1); graficar_frontera(X, d, w, b, umbral, 'AND de 2 entradas');
[X, d] = compuerta('OR', 2, salida);
[w, b] = perceptron(X, d, regla, alpha, umbral, salida, max_epocas, semilla);
subplot(1,2,2); graficar_frontera(X, d, w, b, umbral, 'OR de 2 entradas');

%% Reporte 1: las tres reglas en AND y OR de 2, 3 y 4 entradas
% Promedio de epocas sobre 20 semillas
compuertas = {'AND','OR'};
entradas = [2 3 4];
semillas = 1:20;
R1 = table();
for c = 1:2
    for n = entradas
        [X, d] = compuerta(compuertas{c}, n, salida);
        for r = 1:3
            ep = zeros(1, 20); conv = ep;
            for s = semillas
                [~, ~, ep(s), conv(s)] = perceptron(X, d, r, alpha, umbral, salida, max_epocas, s);
            end
            R1 = [R1; table(compuertas(c), n, r, mean(ep), min(ep), max(ep), 100*mean(conv), ...
                  'VariableNames', {'Compuerta','Entradas','Regla','Epocas_prom','Epocas_min','Epocas_max','Convergio_pct'})];
        end
    end
end
R1

%% Reporte 2: efecto de alpha con la regla 3
alphas = [0.01 0.05 0.1 0.3 0.5 1];
R2 = table();
for c = 1:2
    for n = entradas
        [X, d] = compuerta(compuertas{c}, n, salida);
        for a = alphas
            ep = zeros(1, 20);
            for s = semillas
                [~, ~, ep(s)] = perceptron(X, d, 3, a, umbral, salida, max_epocas, s);
            end
            R2 = [R2; table(compuertas(c), n, a, mean(ep), 'VariableNames', {'Compuerta','Entradas','Alpha','Epocas_prom'})];
        end
    end
end
R2

figure
for c = 1:2
    subplot(1,2,c); hold on
    for n = entradas
        k = strcmp(R2.Compuerta, compuertas{c}) & R2.Entradas == n;
        plot(R2.Alpha(k), R2.Epocas_prom(k), '-o', 'DisplayName', sprintf('%d entradas', n));
    end
    set(gca, 'XScale', 'log'); grid on; legend
    xlabel('alpha'); ylabel('epocas promedio'); title(compuertas{c});
end

%% Reporte 3: efecto del umbral (2 entradas)
umbrales = [-1 -0.5 0 0.5 1 2];
R3 = table();
for c = 1:2
    [X, d] = compuerta(compuertas{c}, 2, salida);
    for u = umbrales
        ep = zeros(1, 20);
        for s = semillas
            [~, ~, ep(s)] = perceptron(X, d, regla, alpha, u, salida, max_epocas, s);
        end
        R3 = [R3; table(compuertas(c), u, mean(ep), 'VariableNames', {'Compuerta','Umbral','Epocas_prom'})];
    end
end
R3

%% Reporte 4: salida en {0,1} en vez de {-1,1}
% Con la regla 1 y d = 0 la correccion es cero, la neurona no aprende esos patrones
R4 = table();
for cod = {[-1 1], [0 1]}
    for c = 1:2
        [X, d] = compuerta(compuertas{c}, 2, cod{1});
        for r = 1:3
            ep = zeros(1, 20); conv = ep;
            for s = semillas
                [~, ~, ep(s), conv(s)] = perceptron(X, d, r, alpha, umbral, cod{1}, max_epocas, s);
            end
            R4 = [R4; table({mat2str(cod{1})}, compuertas(c), r, mean(ep), 100*mean(conv), ...
                  'VariableNames', {'Salida','Compuerta','Regla','Epocas_prom','Convergio_pct'})];
        end
    end
end
R4
