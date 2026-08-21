function guardar_fig(fig, carpeta, nombre)
% Guarda la figura en PNG (fondo blanco) y la cierra, para poder correr los
% scripts de corrido sin llenar la pantalla de ventanas.
if ~exist(carpeta, 'dir'), mkdir(carpeta); end

% en R2025a+ las figuras salen con tema oscuro por defecto y para el informe
% se ven mejor en claro
try
    fig.Theme = 'light';
catch
    set(fig, 'Color', 'w');
end
drawnow;

exportgraphics(fig, fullfile(carpeta, [nombre '.png']), ...
               'Resolution', 150, 'BackgroundColor', 'white');
close(fig);
end
