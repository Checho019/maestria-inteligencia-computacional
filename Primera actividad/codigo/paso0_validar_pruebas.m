%% =======================================================================
%  Validacion de las dos pruebas de normalidad que tocó programar a mano
%
%  MATLAB no trae Shapiro-Wilk ni D'Agostino-Pearson, asi que estan escritas
%  en funciones/swtest.m y funciones/dagostino_k2.m. Antes de usarlas en el
%  analisis hay que comprobar que funcionan, y se comprueba con MATLAB mismo,
%  por simulacion, sin depender de ninguna otra herramienta.
%
%  Dos comprobaciones:
%
%   1. Calibracion. Si los datos SI son normales, una prueba bien hecha debe
%      rechazar la normalidad aproximadamente alfa por ciento de las veces.
%      Si rechaza mucho mas, es alarmista; si rechaza mucho menos, es sorda.
%      Ademas sus p valores deben repartirse uniformemente entre 0 y 1.
%
%   2. Potencia. Si los datos NO son normales, debe rechazar muchas veces.
%      Aca se comparan las dos funciones propias contra lillietest y adtest,
%      que si vienen con MATLAB, para ver si dan resultados del mismo orden.
% =======================================================================
clear; clc; close all;
rng(1);

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'validacion');
xls_e   = fullfile(base, 'Resultados_Ecoli.xlsx');
xls_b   = fullfile(base, 'Resultados_Bank.xlsx');

warning('off','stats:lillietest:OutOfRangePLow');
warning('off','stats:adtest:OutOfRangePLow');
warning('off','stats:lillietest:OutOfRangePHigh');
warning('off','stats:adtest:OutOfRangePHigh');

R      = 2000;                 % repeticiones por escenario
alfa   = 0.05;
tam    = [30 100 336];         % 336 es el tamano del dataset Ecoli
pruebas = {'Shapiro-Wilk (propia)','DAgostino K2 (propia)','Lilliefors (MATLAB)','Anderson-Darling (MATLAB)'};

fprintf('Simulando %d repeticiones por escenario. Esto tarda un par de minutos.\n\n', R);

%% --- 1. Calibracion con datos que si son normales ----------------------
filas = {};
P_guardado = [];
for t = 1:numel(tam)
    n = tam(t);
    P = nan(R, 4);
    for r = 1:R
        x = randn(n, 1);
        P(r,1) = swtest(x);
        P(r,2) = dagostino_k2(x);
        [~, P(r,3)] = lillietest(x);
        [~, P(r,4)] = adtest(x);
    end
    if n == 336, P_guardado = P; end

    for k = 1:4
        p = P(:,k);
        tasa = mean(p < alfa);
        % los p valores deberian repartirse uniforme entre 0 y 1
        [~, p_unif] = kstest(p, 'CDF', makedist('Uniform', 'lower', 0, 'upper', 1));
        filas(end+1,:) = {pruebas{k}, n, tasa, alfa, tasa - alfa, p_unif};  %#ok<SAGROW>
    end
end
Calib = cell2table(filas, 'VariableNames', ...
    {'Prueba','n','Tasa_rechazo_H0','Nominal','Desvio','p_uniformidad'});
disp('--- Calibracion: cuantas veces rechaza cuando NO deberia ---');
disp(Calib);

%% --- 2. Potencia con datos que no son normales -------------------------
% Cuatro formas de salirse de la normal, cada una por un motivo distinto:
%   exponencial  es asimetria fuerte
%   uniforme     es colas cortas, sin pico central
%   t de Student es colas pesadas
%   lognormal suave es asimetria leve, el caso dificil de detectar
%
% Se prueba con los tres tamanos porque con n grande todas las pruebas
% detectan casi todo y no se distinguen. Donde se ve la diferencia es con
% muestras chicas, que es justamente el caso de Ecoli.
alternativas = {'Exponencial','Uniforme','t de Student (5 gl)','Lognormal(0, 0.25)'};
filas = {};
Pot30 = nan(numel(alternativas), 4);
for t = 1:numel(tam)
    n = tam(t);
    for a = 1:numel(alternativas)
        P = nan(R, 4);
        for r = 1:R
            switch a
                case 1, x = exprnd(1, n, 1);
                case 2, x = rand(n, 1);
                case 3, x = trnd(5, n, 1);
                case 4, x = lognrnd(0, 0.25, n, 1);
            end
            P(r,1) = swtest(x);
            P(r,2) = dagostino_k2(x);
            [~, P(r,3)] = lillietest(x);
            [~, P(r,4)] = adtest(x);
        end
        pot = mean(P < alfa);
        if n == 30, Pot30(a,:) = pot; end
        for k = 1:4
            filas(end+1,:) = {alternativas{a}, n, pruebas{k}, pot(k)};  %#ok<SAGROW>
        end
    end
end
Potencia = cell2table(filas, 'VariableNames', {'Distribucion','n','Prueba','Potencia'});
disp('--- Potencia con n = 30, que es donde se separan ---');
disp(unstack(Potencia(Potencia.n == 30, {'Distribucion','Prueba','Potencia'}), ...
             'Potencia', 'Prueba'));
disp('--- Potencia con n = 336 ---');
disp(unstack(Potencia(Potencia.n == 336, {'Distribucion','Prueba','Potencia'}), ...
             'Potencia', 'Prueba'));

%% --- 3. Graficos -------------------------------------------------------
f = figure('Visible','off','Position',[100 100 1150 620]);
for k = 1:4
    subplot(2,2,k);
    histogram(P_guardado(:,k), 20, 'Normalization','probability', ...
              'FaceColor',[0.35 0.6 0.75]);
    hold on; yline(1/20, 'r--', 'LineWidth', 1.2);
    ylim([0 0.12]); xlabel('p valor'); ylabel('proporcion');
    title(sprintf('%s  (rechaza %.1f%%)', pruebas{k}, 100*mean(P_guardado(:,k) < alfa)), ...
          'FontSize', 9);
end
sgtitle(sprintf(['Reparto de los p valores cuando los datos SI son normales ' ...
                 '(n = 336, %d repeticiones)'], R));
guardar_fig(f, dir_fig, '01_calibracion_pvalores');

f = figure('Visible','off','Position',[100 100 1000 470]);
bar(100*Pot30); ylim([0 105]); grid on;
set(gca, 'XTickLabel', alternativas, 'XTickLabelRotation', 12);
ylabel('porcentaje de veces que detecta la no normalidad');
legend(pruebas, 'Location','southoutside', 'Orientation','horizontal', 'FontSize', 8);
title(sprintf(['Potencia con n = 30 y alfa = 0.05 (%d repeticiones). ' ...
               'Con n grande todas llegan al 100%% y no se distinguen.'], R));
guardar_fig(f, dir_fig, '02_potencia');

%% --- 4. Exportar a los dos libros de Excel -----------------------------
for xls = {xls_e, xls_b}
    writetable(Calib,    xls{1}, 'Sheet', '00_Validacion_calibracion');
    writetable(Potencia, xls{1}, 'Sheet', '00_Validacion_potencia');
end
fprintf('\nPaso 0 (validacion de las pruebas propias) terminado.\n');
