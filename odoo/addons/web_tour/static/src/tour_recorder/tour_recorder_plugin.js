import { onWillStart, Plugin, usePlugin, whenReady } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { browser } from "@web/core/browser/browser";
import { OverlayPlugin } from "@web/core/overlay/overlay_plugin";
import { services } from "@web/core/services";
import { session } from "@web/session";
import { TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY, tourRecorderState } from "./tour_recorder_state";

export class TourRecorderPlugin extends Plugin {
    overlay = usePlugin(OverlayPlugin);
    removeTourRecorder = () => {};

    setup() {
        onWillStart(() => this.bootstrap());
    }

    async bootstrap() {
        await whenReady();
        if (
            !window.frameElement &&
            browser.localStorage.getItem(TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY) &&
            !session.is_public
        ) {
            await this.addTourRecorderToOverlay();
        }
    }

    /**
     * Add tour recorder component in overlay container.
     */
    async addTourRecorderToOverlay() {
        const moduleName = "@web_tour/tour_recorder/tour_recorder";
        if (!odoo.loader.modules.get(moduleName)) {
            await loadBundle("web_tour.recorder");
        }
        const deadline = Date.now() + 5000;
        while (!odoo.loader.modules.get(moduleName) && Date.now() < deadline) {
            odoo.loader.startModules();
            await new Promise((r) => setTimeout(r, 50));
        }
        const recorderModule = odoo.loader.modules.get(moduleName);
        if (!recorderModule?.TourRecorder) {
            browser.localStorage.removeItem(TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY);
            tourRecorderState.clear();
            return;
        }
        const { TourRecorder } = recorderModule;
        const remove = this.overlay.add(
            TourRecorder,
            {
                onClose: () => {
                    remove();
                    browser.localStorage.removeItem(TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY);
                    tourRecorderState.clear();
                },
            },
            { sequence: 99999 }
        );

        this.removeTourRecorder = () => {
            remove();
            browser.localStorage.removeItem(TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY);
            tourRecorderState.clear();
        };
    }

    async startTourRecorder() {
        if (!browser.localStorage.getItem(TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY)) {
            await this.addTourRecorderToOverlay();
        }
        browser.localStorage.setItem(TOUR_RECORDER_ACTIVE_LOCAL_STORAGE_KEY, "1");
    }
}

services.add(TourRecorderPlugin);
