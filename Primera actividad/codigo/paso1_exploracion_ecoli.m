%% =======================================================================
%  ECOLI - Paso 0: carga, tipificacion, descriptivos y graficos iniciales
%  Corresponde a la seccion 1 y 11 de la guia de pruebas estadisticas.
% =======================================================================
clear; clc; close all;

base = fileparts(fileparts(mfilename('fullpath')));   % carpeta "Primera actividad"
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'ecoli', 'figuras');
xls     = fullfile(base, 'Resultados_Ecoli.xlsx');

%% --- 1. Carga -----------------------------------------------------------
% El archivo viene separado por espacios en blanco de ancho variable.
archivo = fullfile(base, 'data', 'ecoli', 'ecoli.data');
T = readtable(archivo, 'FileType','text', 'Delimiter',' ', ...
              'ConsecutiveDelimitersRule','join', ...
              'LeadingDelimitersRule','ignore', 'ReadVariableNames',false);
T.Properties.VariableNames = {'secuencia','mcg','gvh','lip','chg','aac','alm1','alm2','clase'};

% la primera columna es un identificador de proteina, no sirve para clasificar
T.secuencia = [];

vars   = {'mcg','gvh','lip','chg','aac','alm1','alm2'};
contin = {'mcg','gvh','aac','alm1','alm2'};       % continuas [0,1]
binar  = {'lip','chg'};                            % binarias segun el .names
X      = T{:, vars};
y      = T.clase;
clases = unique(y);

fprintf('Ecoli cargado: %d muestras, %d predictoras, %d clases\n', ...
        height(T), numel(vars), numel(clases));

%% --- 2. Valores faltantes ----------------------------------------------
n_falt = sum(ismissing(T{:, vars}), 1)';
fprintf('Valores faltantes en total: %d\n', sum(n_falt));

%% --- 3. Estadisticos descriptivos --------------------------------------
Desc = table(vars', ...
    mean(X)', median(X)', std(X)', var(X)', min(X)', max(X)', ...
    (quantile(X,0.75) - quantile(X,0.25))', ...
    skewness(X)', kurtosis(X)', arrayfun(@(j) numel(unique(X(:,j))), (1:numel(vars))'), n_falt, ...
    'VariableNames', {'Variable','Media','Mediana','Desv','Varianza','Min','Max', ...
                      'IQR','Asimetria','Curtosis','N_unicos','Faltantes'});
disp(Desc);

% chg practicamente no varia: casi todas las filas valen lo mismo
for j = 1:numel(vars)
    [c, v] = groupcounts(X(:, j));
    if max(c)/height(T) > 0.98
        fprintf('OJO: %s tiene el %.1f%% de los datos en el valor %.2f (varianza casi nula)\n', ...
                vars{j}, 100*max(c)/height(T), v(c == max(c)));
    end
end

%% --- 4. Balance de la variable objetivo (seccion 11 de la guia) ---------
[cnt, nom] = groupcounts(y);
n = numel(y);  k = numel(nom);
esperado = n/k;
chi2_bal = sum((cnt - esperado).^2 / esperado);        % bondad de ajuste vs uniforme
p_bal    = chi2cdf(chi2_bal, k-1, 'upper');
IR       = max(cnt)/min(cnt);                           % imbalance ratio
H        = -sum((cnt/n) .* log(cnt/n)) / log(k);        % entropia normalizada (1 = perfecto)

Balance = table(nom, cnt, 100*cnt/n, repmat(esperado,k,1), ...
    'VariableNames', {'Clase','N','Porcentaje','EsperadoUniforme'});
disp(Balance);
fprintf('Chi2 bondad de ajuste = %.2f (gl=%d), p = %.3g\n', chi2_bal, k-1, p_bal);
fprintf('Razon de desbalance (IR) = %.1f | Entropia normalizada = %.3f\n', IR, H);

Resumen_bal = table({'chi2';'gl';'p_valor';'IR_max_min';'Entropia_norm';'N_total';'N_clases'}, ...
                    [chi2_bal; k-1; p_bal; IR; H; n; k], ...
                    'VariableNames', {'Indicador','Valor'});

%% --- 5. Graficos iniciales ---------------------------------------------
% 5.1 histogramas de cada predictora
f = figure('Visible','off','Position',[100 100 1100 600]);
for j = 1:numel(vars)
    subplot(2,4,j);
    histogram(X(:,j), 20, 'FaceColor',[0.2 0.5 0.8]);
    title(vars{j}); xlabel(''); ylabel('frec');
end
sgtitle('Ecoli - histogramas de las variables predictoras (dato crudo)');
guardar_fig(f, dir_fig, '01_histogramas_crudo');

% 5.2 boxplot general (regla 1.5*IQR -> outliers marcados en rojo)
f = figure('Visible','off','Position',[100 100 800 450]);
boxplot(X, 'Labels', vars);
title('Ecoli - boxplot de las predictoras (dato crudo)'); ylabel('valor');
guardar_fig(f, dir_fig, '02_boxplot_crudo');

% 5.3 conteo de clases
f = figure('Visible','off','Position',[100 100 700 420]);
bar(categorical(nom, nom), cnt, 'FaceColor',[0.85 0.4 0.3]);
hold on; yline(esperado,'--k','esperado si fuera uniforme');
title('Ecoli - distribucion de la clase (8 clases, muy desbalanceada)');
ylabel('numero de muestras'); xlabel('sitio de localizacion');
text(1:k, cnt+3, string(cnt), 'HorizontalAlignment','center');
guardar_fig(f, dir_fig, '03_balance_clases_crudo');

% 5.4 boxplot por clase de cada variable continua
f = figure('Visible','off','Position',[100 100 1200 650]);
for j = 1:numel(contin)
    subplot(2,3,j);
    boxplot(T.(contin{j}), y);
    title(contin{j}); ylabel('valor');
end
sgtitle('Ecoli - boxplots por clase (respaldo visual de Kruskal-Wallis/ANOVA)');
guardar_fig(f, dir_fig, '04_boxplot_por_clase');

% 5.5 Q-Q plots (complemento visual de las pruebas de normalidad)
f = figure('Visible','off','Position',[100 100 1100 600]);
for j = 1:numel(contin)
    subplot(2,3,j);
    qqplot(T.(contin{j}));
    title(contin{j}); xlabel('cuantiles teoricos'); ylabel('muestra');
end
sgtitle('Ecoli - Q-Q plots contra la normal');
guardar_fig(f, dir_fig, '05_qqplots');

% 5.6 matriz de dispersion coloreada por clase
f = figure('Visible','off','Position',[100 100 1000 900]);
gplotmatrix(T{:, contin}, [], y, [], [], 6, 'on', 'grpbars', contin);
title('Ecoli - matriz de dispersion por clase');
guardar_fig(f, dir_fig, '06_scatter_matrix');

%% --- 6. Exportar a Excel -----------------------------------------------
writetable(Desc,        xls, 'Sheet', 'E1_Descriptivos');
writetable(Balance,     xls, 'Sheet', 'E1_Balance_clase');
writetable(Resumen_bal, xls, 'Sheet', 'E1_Balance_test');

save(fullfile(base,'resultados','ecoli','ecoli_crudo.mat'), 'T','X','y','vars','contin','binar','clases');
fprintf('\nPaso 1 (exploracion) terminado.\n');
