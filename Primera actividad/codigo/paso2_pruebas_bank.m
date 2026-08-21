%% =======================================================================
%  BANK MARKETING - Pruebas estadisticas sobre las variables
%
%  Aqui el tamano de muestra cambia las decisiones respecto a Ecoli:
%   - n = 45211, o sea que Shapiro-Wilk queda fuera de rango (vale hasta
%     ~5000). Se corre sobre una submuestra aleatoria y se acompana con
%     Lilliefors y Anderson-Darling sobre el total.
%   - con esta n cualquier diferencia minima sale significativa, asi que el
%     p-valor por si solo no sirve: hay que mirar el tamano del efecto.
% =======================================================================
clear; clc; close all;
rng(42);

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'bank', 'figuras');
xls     = fullfile(base, 'Resultados_Bank.xlsx');
load(fullfile(base, 'resultados', 'bank', 'bank_crudo.mat'));

warning('off','stats:lillietest:OutOfRangePLow');
warning('off','stats:adtest:OutOfRangePLow');

alfa = 0.05;
X    = T{:, num};
nn   = numel(num);
es_si = strcmp(y, 'yes');

%% --- 2. Normalidad (guia seccion 2) ------------------------------------
n_sub = 5000;                       % tope practico de Shapiro-Wilk
sub   = randperm(height(T), n_sub);

R = nan(nn, 7);
for j = 1:nn
    x = X(:, j);
    p_sw  = swtest(x(sub));
    [~, p_lil] = lillietest(x, 'MCTol', 0.01);
    [~, p_ad]  = adtest(x);
    p_k2  = dagostino_k2(x);
    R(j, :) = [p_sw, p_lil, p_ad, p_k2, skewness(x), kurtosis(x), 0];
end
Norm = table(num', R(:,1), R(:,2), R(:,3), R(:,4), R(:,5), R(:,6), R(:,1) > alfa, ...
    'VariableNames', {'Variable','p_Shapiro_sub5000','p_Lilliefors','p_AndersonD', ...
                      'p_DAgostino','Asimetria','Curtosis','Normal_alfa05'});
disp('--- Normalidad ---'); disp(Norm);
fprintf('Variables que pasan normalidad: %d de %d\n', sum(Norm.Normal_alfa05), nn);

%% --- 3. Homocedasticidad entre las dos clases (guia seccion 3) ---------
V = nan(nn, 2);
for j = 1:nn
    V(j,1) = vartestn(X(:,j), y, 'TestType','LeveneAbsolute', 'Display','off');
    V(j,2) = vartestn(X(:,j), y, 'TestType','Bartlett',       'Display','off');
end
Var = table(num', V(:,1), V(:,1) > alfa, V(:,2), V(:,2) > alfa, ...
    'VariableNames', {'Variable','p_Levene','Homoced_Levene','p_Bartlett','Homoced_Bartlett'});
disp('--- Homogeneidad de varianzas (yes vs no) ---'); disp(Var);

%% --- 4. Comparacion entre las dos clases (guia seccion 4) --------------
% Se corren las tres: Student, Welch y Mann-Whitney. Y sobre todo se calcula
% el tamano del efecto, que es lo unico que distingue "diferencia real" de
% "diferencia detectable porque tengo 45 mil datos".
C = nan(nn, 6);
for j = 1:nn
    a = X(es_si, j);  b = X(~es_si, j);
    [~, p_stu] = ttest2(a, b);
    [~, p_wel] = ttest2(a, b, 'Vartype','unequal');
    [p_mw, ~, st] = ranksum(a, b);

    % d de Cohen con desviacion combinada
    n1 = numel(a); n2 = numel(b);
    s_comb = sqrt(((n1-1)*var(a) + (n2-1)*var(b)) / (n1+n2-2));
    d = (mean(a) - mean(b)) / s_comb;

    % correlacion biserial por rangos, a partir de la U de Mann-Whitney
    U1 = st.ranksum - n1*(n1+1)/2;
    r_rb = 2*U1/(n1*n2) - 1;

    C(j, :) = [p_stu, p_wel, p_mw, d, r_rb, mean(a)-mean(b)];
end
Comp = table(num', C(:,6), C(:,1), C(:,2), C(:,3), C(:,4), C(:,5), abs(C(:,4)) >= 0.2, ...
    'VariableNames', {'Variable','Dif_medias','p_tStudent','p_tWelch','p_MannWhitney', ...
                      'd_Cohen','r_rangobiserial','Efecto_al_menos_pequeno'});
disp('--- Comparacion yes vs no ---'); disp(Comp);
fprintf('Significativas con alfa=0.05 (Welch): %d de %d\n', sum(Comp.p_tWelch < alfa, 'omitnan'), nn);
fprintf('Con efecto al menos pequeno (|d|>=0.2): %d de %d\n', sum(Comp.Efecto_al_menos_pequeno), nn);

%% --- 5. Categoricas vs clase (guia seccion 7) -------------------------
filas = {};
for j = 1:numel(cat)
    [Vcr, chi2v, pv, gl] = cramersv(T.(cat{j}), y);
    tabla = crosstab(T.(cat{j}), y);
    esp   = sum(tabla,2)*sum(tabla,1)/sum(tabla(:));
    min_esp = min(esp(:));
    % El test exacto de Fisher solo hace falta cuando alguna celda esperada
    % queda por debajo de 5. Aca no pasa en ninguna, asi que basta el chi2.
    usa_fisher = min_esp < 5 && all(size(tabla) == [2 2]);
    p_fisher = NaN;
    if usa_fisher
        [~, p_fisher] = fishertest(tabla);
    end
    filas(end+1,:) = {cat{j}, size(tabla,1), chi2v, gl, pv, Vcr, min_esp, ...
                      min_esp >= 5, p_fisher};   %#ok<SAGROW>
end
Cat = cell2table(filas, 'VariableNames', ...
    {'Variable','N_niveles','Chi2','gl','p_valor','V_Cramer','MinEsperado', ...
     'Cumple_regla_5','p_Fisher'});
Cat = sortrows(Cat, 'V_Cramer', 'descend');
disp('--- Categoricas vs clase (ordenadas por V de Cramer) ---'); disp(Cat);

%% --- 6. Correlacion y multicolinealidad (guia secciones 6 y 9) --------
Rp = corr(X, 'type','Pearson');
Rs = corr(X, 'type','Spearman');
vif = calcular_vif(X);
cond_num = cond(zscore(X));

Corr_P = array2table(Rp, 'VariableNames', num, 'RowNames', num);
Corr_S = array2table(Rs, 'VariableNames', num, 'RowNames', num);
Vif    = table(num', vif, vif > 5, 'VariableNames', {'Variable','VIF','Sospechosa'});
fprintf('Numero de condicion: %.1f\n', cond_num);
disp('--- VIF ---'); disp(Vif);

f = figure('Visible','off','Position',[100 100 1150 480]);
subplot(1,2,1); imagesc(Rp, [-1 1]); colorbar; axis square;
set(gca,'XTick',1:nn,'XTickLabel',num,'YTick',1:nn,'YTickLabel',num,'XTickLabelRotation',45);
title('Pearson');
for a = 1:nn
    for b = 1:nn
        text(b, a, sprintf('%.2f', Rp(a,b)), 'HorizontalAlignment','center','FontSize',7);
    end
end
subplot(1,2,2); imagesc(Rs, [-1 1]); colorbar; axis square;
set(gca,'XTick',1:nn,'XTickLabel',num,'YTick',1:nn,'YTickLabel',num,'XTickLabelRotation',45);
title('Spearman');
for a = 1:nn
    for b = 1:nn
        text(b, a, sprintf('%.2f', Rs(a,b)), 'HorizontalAlignment','center','FontSize',7);
    end
end
sgtitle('Bank - mapas de calor de correlacion entre numericas');
guardar_fig(f, dir_fig, '07_correlacion');

%% --- 7. Relevancia frente a la clase (guia seccion 8) -----------------
% MRMR acepta tablas mixtas, asi que se le pasan numericas y categoricas
% juntas y devuelve un ranking unico comparable entre los dos tipos.
Tm = T(:, [num cat]);
for j = 1:numel(cat), Tm.(cat{j}) = categorical(Tm.(cat{j})); end
% ojo: fscmrmr devuelve los scores en el orden ORIGINAL de las columnas,
% asi que para el ranking hay que reordenarlos con sc(idx).
[idx_mrmr, sc_mrmr] = fscmrmr(Tm, y);
sc_ord = sc_mrmr(idx_mrmr);
Rel = table(Tm.Properties.VariableNames(idx_mrmr)', sc_ord', (1:width(Tm))', ...
    'VariableNames', {'Variable','Score_MRMR','Ranking'});
disp('--- Ranking de relevancia (MRMR, numericas y categoricas juntas) ---');
disp(Rel);

f = figure('Visible','off','Position',[100 100 900 450]);
barh(flipud(sc_ord'), 'FaceColor',[0.35 0.6 0.75]);
set(gca,'YTick',1:width(Tm),'YTickLabel',flipud(Rel.Variable));
xlabel('score MRMR'); title('Bank - relevancia de cada variable frente a la clase');
grid on;
guardar_fig(f, dir_fig, '08_relevancia_mrmr');

%% --- 8. Outliers (guia seccion 10) ------------------------------------
O = nan(nn, 5);
for j = 1:nn
    x = X(:, j);
    q = quantile(x, [0.25 0.75]);  ri = q(2)-q(1);
    n_iqr = sum(x < q(1)-1.5*ri | x > q(2)+1.5*ri);
    n_z   = sum(abs((x - mean(x))/std(x)) > 3);
    O(j,:) = [ri, n_iqr, 100*n_iqr/numel(x), n_z, 100*n_z/numel(x)];
end
Out = table(num', O(:,1), O(:,2), O(:,3), O(:,4), O(:,5), O(:,1) == 0, ...
    'VariableNames', {'Variable','IQR','N_out_IQR','Pct_IQR','N_out_Zscore', ...
                      'Pct_Zscore','IQR_cero'});
disp('--- Outliers univariados ---'); disp(Out);

% Detalle importante: pdays y previous tienen IQR = 0 porque mas del 75% de
% los registros valen lo mismo (-1 y 0 respectivamente). Con IQR = 0 la regla
% de Tukey marca como atipico TODO valor distinto del cuartil, y winsorizar
% dejaria la variable convertida en una constante. A esas dos no se les
% aplica la regla; se tratan aparte en el paso 3.
if any(Out.IQR_cero)
    fprintf('Variables con IQR = 0 (la regla 1.5*IQR no aplica): %s\n', ...
            strjoin(Out.Variable(Out.IQR_cero)', ', '));
end

filas_con_out = false(height(T),1);
for j = 1:nn
    q = quantile(X(:,j), [0.25 0.75]);  ri = q(2)-q(1);
    filas_con_out = filas_con_out | X(:,j) < q(1)-1.5*ri | X(:,j) > q(2)+1.5*ri;
end
fprintf(['Filas con al menos un atipico: %d (%.1f%%). Borrarlas seria perder ' ...
         'casi la mitad del dataset, por eso se winsoriza.\n'], ...
        sum(filas_con_out), 100*mean(filas_con_out));

%% --- 9. PCA para separabilidad global (guia seccion 13.7) -------------
[~, score, ~, ~, expl] = pca(zscore(X));
f = figure('Visible','off','Position',[100 100 1150 450]);
subplot(1,2,1);
% se dibuja una muestra de 4000 puntos porque 45 mil satura el scatter
mu = randperm(height(T), 4000);
gscatter(score(mu,1), score(mu,2), y(mu), [0.7 0.7 0.7; 0.85 0.2 0.2], '.o', [6 4]);
xlabel(sprintf('CP1 (%.1f%%)', expl(1))); ylabel(sprintf('CP2 (%.1f%%)', expl(2)));
title('Muestra de 4000 clientes'); grid on;
subplot(1,2,2);
bar(expl); hold on; plot(cumsum(expl), '-o', 'LineWidth', 1.2);
xlabel('componente'); ylabel('% de varianza'); legend('individual','acumulada','Location','east');
title('Varianza explicada'); grid on;
sgtitle('Bank - PCA sobre las 7 numericas');
guardar_fig(f, dir_fig, '09_pca');

%% --- 10. Exportar -----------------------------------------------------
writetable(Norm,   xls, 'Sheet', 'B2_Normalidad');
writetable(Var,    xls, 'Sheet', 'B2_Varianzas');
writetable(Comp,   xls, 'Sheet', 'B2_Comparacion');
writetable(Cat,    xls, 'Sheet', 'B2_Categoricas');
writetable(Corr_P, xls, 'Sheet', 'B2_Corr_Pearson',  'WriteRowNames', true);
writetable(Corr_S, xls, 'Sheet', 'B2_Corr_Spearman', 'WriteRowNames', true);
writetable(Vif,    xls, 'Sheet', 'B2_VIF');
writetable(Rel,    xls, 'Sheet', 'B2_Relevancia');
writetable(Out,    xls, 'Sheet', 'B2_Outliers');

save(fullfile(base,'resultados','bank','bank_pruebas.mat'), ...
     'Norm','Var','Comp','Cat','Rel','Out','vif','cond_num');
fprintf('\nPaso 2 (pruebas bank) terminado.\n');
